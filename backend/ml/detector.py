import pickle, numpy as np
from feature_extractor import extract, FEATURES

with open("models/isolation_forest.pkl", "rb") as f:
    _bundle = pickle.load(f)
_model  = _bundle["model"]
_scaler = _bundle["scaler"]

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
    X = np.array(features).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    raw_score = _model.decision_function(X_scaled)[0]
    _score_history.append(raw_score)

    mn, mx = min(_score_history), max(_score_history)
    if mx == mn:
        risk = 0.5
    else:
        risk = 1 - (raw_score - mn) / (mx - mn)

    threat_type = _classify_threat(features)

    return {
        "risk_score": round(risk, 3),
        "threat_type": threat_type,
        "features": dict(zip(FEATURES, features)),
        "flag": risk > 0.75
    }

def _classify_threat(features: list) -> str:
    "Rule-based layer on top of IF score — gives human-readable type"
    req_pm, uniq_ips, fails, payload, token_reuse, variety, hour = features
    if token_reuse > 10:          return "token_replay"
    if req_pm > 150:              return "rate_flood"
    if fails > 10:               return "credential_stuffing"
    if variety > 20:             return "endpoint_scraping"
    if uniq_ips > 8:             return "distributed_attack"
    return "anomaly"