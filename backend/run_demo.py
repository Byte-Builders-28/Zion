"""
Demo runner for Zion backend.
- Runs normal + attack traffic (token replay and rate flood)
- Exports collected logs to SQLite
- Retrains the IsolationForest on recent logs (optional)
- Exercises Smallify fallback for resilience
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Local imports
from ml.feature_extractor import FEATURES, reset_state
from policy.smolify_client import generate_policy

ROOT = Path(__file__).resolve().parent
BASE_URL_DEFAULT = os.getenv("DEMO_BASE_URL", "http://127.0.0.1:8000")
SQLITE_PATH_DEFAULT = ROOT / "data" / "demo_logs.sqlite"
MODEL_PATH = ROOT / "ml" / "models" / "isolation_forest.pkl"

# Traffic profiles
TOKEN = "eyJhbGc.stolen.token.123"


def _ping(base_url: str, timeout: float = 3.0) -> bool:
    try:
        resp = requests.get(f"{base_url}/test", timeout=timeout)
        return resp.status_code < 500
    except Exception:
        return False


def _start_server() -> subprocess.Popen:
    """Start uvicorn in the background if not already running."""
    env = os.environ.copy()
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    return subprocess.Popen(cmd, cwd=ROOT)


def _stop_server(proc: subprocess.Popen | None):
    if proc is None:
        return
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=10)
    except Exception:
        proc.kill()


def _clear_backend_state(base_url: str):
    reset_state()  # clear sliding window state in feature extractor
    try:
        requests.post(f"{base_url}/events/clear-logs", timeout=5)
    except Exception:
        pass


def _blast_requests(total: int, workers: int, fn) -> Tuple[int, int]:
    """Run the given callable total times using a pool."""
    success = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for ok in executor.map(fn, range(total)):
            if ok:
                success += 1
            else:
                failed += 1
    return success, failed


def run_normal(base_url: str, total: int = 80):
    def _send(_: int):
        try:
            val = int(time.time() * 1000) % 10000
            requests.post(
                f"{base_url}/test?id={val}",
                json={"user": f"guest_{val}", "data": "clean"},
                timeout=5,
            )
            return True
        except Exception:
            return False

    return _blast_requests(total=total, workers=10, fn=_send)


def run_token_replay(base_url: str, total: int = 200, workers: int = 20):
    def _send(i: int):
        headers = {"Authorization": f"Bearer {TOKEN}"}
        payload = {"user": "admin", "password": f"pass{i}"}
        try:
            requests.post(f"{base_url}/login", headers=headers, json=payload, timeout=5)
            return True
        except Exception:
            return False

    return _blast_requests(total=total, workers=workers, fn=_send)


def run_rate_flood(base_url: str, total: int = 400, workers: int = 40):
    def _send(_: int):
        try:
            requests.get(f"{base_url}/test", timeout=3)
            return True
        except Exception:
            return False

    return _blast_requests(total=total, workers=workers, fn=_send)


def fetch_logs(base_url: str) -> List[dict]:
    try:
        resp = requests.get(f"{base_url}/dashboard/raw_logs", timeout=10)
        data = resp.json()
        if isinstance(data, dict) and data.get("msg") == "no data":
            return []
        return data if isinstance(data, list) else []
    except Exception:
        return []


def export_logs_to_sqlite(logs: List[dict], db_path: Path) -> int:
    if not logs:
        return 0

    records = []
    for log in logs:
        score = log.get("score_result", {}) or {}
        feats = score.get("features", {}) or {}
        record = {
            "endpoint": log.get("endpoint"),
            "method": log.get("method"),
            "ip": log.get("ip"),
            "timestamp": log.get("timestamp"),
            "latency": log.get("latency"),
            "token": log.get("token"),
            "payload_size": log.get("payload_size"),
            "status_code": log.get("status_code"),
            "risk_score": score.get("risk_score"),
            "flag": score.get("flag"),
            "threat_type": score.get("threat_type"),
        }
        for k in FEATURES:
            record[f"feat_{k}"] = feats.get(k)
        records.append(record)

    df = pd.DataFrame(records)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("logs", conn, if_exists="append", index=False)
    return len(df)


def retrain_from_logs(logs: List[dict], model_path: Path) -> dict:
    rows = []
    for log in logs:
        score = log.get("score_result", {}) or {}
        feats = score.get("features", {}) or {}
        if not feats:
            continue
        row = {k: float(feats.get(k, 0.0)) for k in FEATURES}
        row["label"] = 1 if score.get("flag") or score.get("threat_type") != "anomaly" else 0
        rows.append(row)

    if len(rows) < 20:
        return {"trained": False, "reason": "not_enough_samples", "count": len(rows)}

    df = pd.DataFrame(rows)
    normal = df[df["label"] == 0]
    if normal.empty:
        normal = df.copy()

    scaler = StandardScaler()
    X_normal = scaler.fit_transform(normal[FEATURES])

    model = IsolationForest(n_estimators=120, contamination=0.01, random_state=42)
    model.fit(X_normal)

    X_all = scaler.transform(df[FEATURES])
    scores = model.decision_function(X_all)
    mn, mx = float(scores.min()), float(scores.max())

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        json_bundle = {"model": model, "scaler": scaler, "min_score": mn, "max_score": mx}
        import pickle
        pickle.dump(json_bundle, f)

    return {
        "trained": True,
        "count": len(df),
        "normal_samples": len(normal),
        "min_score": mn,
        "max_score": mx,
    }


def exercise_smolify(iterations: int = 10):
    results = []
    for i in range(iterations):
        report = {
            "threat_type": "rate_flood" if i % 2 else "token_replay",
            "endpoint": "/login" if i % 2 else "/test",
            "ip": f"10.0.0.{i}",
            "risk_score": 0.85 if i % 2 else 0.45,
        }
        policy = generate_policy(report)
        results.append(policy)
    return results


def pipeline_run(run_id: int, base_url: str, args) -> dict:
    _clear_backend_state(base_url)

    summary = {"run": run_id, "phases": []}

    # Normal traffic
    ok, fail = run_normal(base_url, total=args.normal)
    summary["phases"].append({"phase": "normal", "ok": ok, "fail": fail})

    # Token replay attack
    ok, fail = run_token_replay(base_url, total=args.token_replay, workers=args.workers)
    summary["phases"].append({"phase": "token_replay", "ok": ok, "fail": fail})

    # Rate flood attack
    ok, fail = run_rate_flood(base_url, total=args.rate_flood, workers=args.workers)
    summary["phases"].append({"phase": "rate_flood", "ok": ok, "fail": fail})

    time.sleep(2)
    logs = fetch_logs(base_url)
    summary["log_count"] = len(logs)

    exported = export_logs_to_sqlite(logs, Path(args.sqlite)) if args.export_logs else 0
    summary["exported"] = exported

    if args.retrain:
        retrain_result = retrain_from_logs(logs, MODEL_PATH)
        summary["retrain"] = retrain_result

    if args.exercise_smolify:
        smolify_results = exercise_smolify(iterations=10)
        summary["smolify"] = {"runs": len(smolify_results)}

    return summary


def main():
    parser = argparse.ArgumentParser(description="Run Zion demo pipeline")
    parser.add_argument("--base-url", default=BASE_URL_DEFAULT, help="Backend base URL")
    parser.add_argument("--pipelines", type=int, default=3, help="Number of consecutive runs")
    parser.add_argument("--normal", type=int, default=80, help="Normal traffic requests")
    parser.add_argument("--token-replay", type=int, default=200, help="Token replay attack requests")
    parser.add_argument("--rate-flood", type=int, default=400, help="Rate flood attack requests")
    parser.add_argument("--workers", type=int, default=30, help="Thread pool size for attacks")
    parser.add_argument("--export-logs", action="store_true", help="Export logs to SQLite")
    parser.add_argument("--sqlite", default=str(SQLITE_PATH_DEFAULT), help="SQLite output path")
    parser.add_argument("--retrain", action="store_true", help="Retrain IsolationForest from recent logs")
    parser.add_argument("--exercise-smolify", action="store_true", help="Call Smallify fallback 10 times")
    parser.add_argument("--no-autostart", action="store_true", help="Skip starting uvicorn automatically")
    parser.add_argument("--dry-run", action="store_true", help="Skip HTTP traffic and just validate flow")

    args = parser.parse_args()

    server_proc = None
    base_url = args.base_url.rstrip("/")

    if not args.dry_run:
        if not _ping(base_url):
            if args.no_autostart:
                print("[!] Backend not reachable and auto-start disabled.")
                sys.exit(1)
            server_proc = _start_server()
            time.sleep(2)
            if not _ping(base_url):
                print("[!] Failed to start backend server.")
                _stop_server(server_proc)
                sys.exit(1)

    try:
        summaries = []
        for i in range(1, args.pipelines + 1):
            if args.dry_run:
                summaries.append({"run": i, "phases": "dry-run"})
                continue
            summary = pipeline_run(i, base_url, args)
            summaries.append(summary)
            time.sleep(1)

        print(json.dumps({"pipelines": summaries}, indent=2))
    finally:
        _stop_server(server_proc)


if __name__ == "__main__":
    main()
