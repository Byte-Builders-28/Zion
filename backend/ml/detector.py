import pickle, os, numpy as np
import pandas as pd
from ml.feature_extractor import extract, FEATURES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "isolation_forest.pkl")

with open(MODEL_PATH, "rb") as f:
    _bundle = pickle.load(f)
_model  = _bundle["model"]
_scaler = _bundle["scaler"]
_min_score = _bundle.get("min_score", -0.1)
_max_score = _bundle.get("max_score", 0.05)

_score_history = []

def score_request(request: dict) -> dict:
    """
    Returns:
    {
        "risk_score": 0.94,       # 0 = normal, 1 = critical
        "threat_type": "rate_flood",
        "features": {...},
        "flag": True
    }
    """
    features = extract(request)
    # Use a DataFrame with column names to match how the scaler was trained
    X_df = pd.DataFrame([features], columns=FEATURES)
    X_scaled = _scaler.transform(X_df)

    raw_score = _model.decision_function(X_scaled)[0]
    _score_history.append(raw_score)

    mn, mx = _min_score, _max_score
    
    # Clip raw_score to mn/mx bounds to keep risk between 0 and 1
    raw_score_clipped = max(min(raw_score, mx), mn)
    
    if mx == mn:
        risk = 0.5
    else:
        risk = 1 - (raw_score_clipped - mn) / (mx - mn)

    # Classify based on initial risk
    threat_type = _classify_threat(features, risk)

    # If this looks like low-volume, clean background traffic but the
    # model is very uncertain (high risk), cap the risk so that
    # harmless one-off requests (e.g., hitting "/") don't look
    # like critical incidents.
    if threat_type == "anomaly":
        req_pm, uniq_ips, fails, payload, token_reuse, variety, hour = features
        if req_pm <= 10 and fails == 0 and token_reuse == 0 and variety <= 5:
            risk = min(risk, 0.3)

    return {
        "risk_score": float(round(risk, 3)),
        "threat_type": str(threat_type),
        "features": {str(k): float(v) for k, v in zip(FEATURES, features)},
        # Only flag when risk is high enough; do not flag all non-anomaly types blindly
        "flag": bool(risk >= 0.75),
        "raw_score": float(raw_score),
        "mn": float(mn),
        "mx": float(mx)
    }

def _classify_threat(features: list, risk: float) -> str:
    """Rule-based layer on top of IF score — gives human-readable type.

    We combine simple heuristics with the anomaly risk so that low-risk
    background traffic (e.g., /docs) tends to stay as "anomaly"/benign
    while strong patterns map to specific attack types.
    """
    req_pm, uniq_ips, fails, payload, token_reuse, variety, hour = features

    # If model thinks this is low risk, keep it generic.
    if risk < 0.4:
        return "anomaly"

    # Token replay: heavy reuse of the same token across many IPs
    if token_reuse >= 5 and uniq_ips >= 3:
        return "token_replay"

    # Rate flood: very high request volume in a short window
    if req_pm >= 120:
        return "rate_flood"

    # Credential stuffing: many failed logins in a short period
    if fails >= 6 and req_pm >= 10:
        return "credential_stuffing"

    # Endpoint scraping: touching many different endpoints from same IP
    if variety >= 15 and req_pm >= 20:
        return "endpoint_scraping"

    # Distributed attack: many IPs sharing same token or high fan-out
    if uniq_ips >= 10:
        return "distributed_attack"

    return "anomaly"