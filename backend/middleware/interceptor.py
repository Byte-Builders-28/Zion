import time
import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse
from queue import Queue

from ml.detector import score_request
from policy.smolify_client import generate_policy
from policy.executor import execute_action, is_blocked, is_rate_limited, is_token_revoked
from blockchain.algorand_logger import log_incident

log_queue = Queue(maxsize=10000)
last_alert_time = 0


def background_threat_handler(score_result: dict, log_data: dict):
    global last_alert_time
    if time.time() - last_alert_time < 10:
        return
    last_alert_time = time.time()

    try:
        policy = generate_policy({
            "threat_type": score_result.get("threat_type"),
            "endpoint":    log_data["endpoint"],
            "ip":          log_data["ip"],
            "risk_score":  score_result.get("risk_score")
        })

        # Execute the AI decision
        execute_action(policy.get("action", "monitor"), {
            "ip":       log_data["ip"],
            "token":    log_data.get("token"),
            "endpoint": log_data["endpoint"],
            "risk":     score_result.get("risk_score", 0.0)
        })

        log_incident({
            "id":       str(int(time.time() * 1000)),
            "type":     score_result.get("threat_type"),
            "endpoint": log_data["endpoint"],
            "ip":       log_data["ip"],
            "risk":     score_result.get("risk_score"),
            "policy":   policy.get("rule_name", "unknown")
        })

        print(f"[Threat Handler] Action: {policy.get('action')} | IP: {log_data['ip']}")

    except Exception as e:
        print(f"[Threat Handler Error] {e}")


def add_log(data: dict):
    try:
        log_queue.put_nowait(data)
    except:
        log_queue.get()
        log_queue.put_nowait(data)


async def interceptor(request: Request, call_next):
    start_time = time.time()

    ip = request.client.host if request.client else "unknown"
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split("Bearer ")[-1] if "Bearer " in auth_header else ""

    # ── Enforcement gate — runs BEFORE processing request ──
    if is_blocked(ip):
        print(f"[Interceptor] BLOCKED request from {ip}")
        return JSONResponse(
            status_code=403,
            content={"detail": "IP blocked by Zion security policy"}
        )

    if is_rate_limited(ip):
        print(f"[Interceptor] RATE LIMITED request from {ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded — try again later"}
        )

    if token and is_token_revoked(token):
        print(f"[Interceptor] REVOKED TOKEN from {ip}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Token revoked by Zion security policy"}
        )

    # ── Normal request flow ──
    response = await call_next(request)
    process_time = time.time() - start_time

    payload_size = int(request.headers.get("content-length", 0))
    endpoint_path = request.url.path

    endpoint_path = request.url.path

    log_data = {
        "endpoint":     endpoint_path,
        "method":       request.method,
        "ip":           ip,
        "timestamp":    time.time(),
        "latency":      process_time,
        "token":        token,
        "payload_size": payload_size,
        "status_code":  response.status_code
    }

    try:
        # Skip threat scoring for docs endpoints
        if endpoint_path in {"/docs", "/openapi.json", "/redoc"}:
            score_result = {
                "risk_score": 0.0,
                "threat_type": "anomaly",
                "features": {},
                "flag": False,
            }
        else:
            score_result = score_request(log_data)

        log_data["score_result"] = score_result
        print(f"[Interceptor] Score: {score_result.get('risk_score')} | Flag: {score_result.get('flag')} | Type: {score_result.get('threat_type')}")

        if score_result.get("flag"):
            asyncio.create_task(
                asyncio.to_thread(background_threat_handler, score_result, log_data)
            )

    except Exception as e:
        print(f"[Interceptor Error] Threat scoring failed: {e}")
        log_data["score_result"] = {"flag": False, "error": str(e)}

    add_log(log_data)
    return response


def get_batch(max_items=100):
    batch = []
    while not log_queue.empty() and len(batch) < max_items:
        batch.append(log_queue.get())
    return batch