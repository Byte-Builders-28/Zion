import pickle, os, numpy as np
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
    X = np.array(features).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    raw_score = _model.decision_function(X_scaled)[0]
    _score_history.append(raw_score)

    mn, mx = _min_score, _max_score
    
    # Clip raw_score to mn/mx bounds to keep risk between 0 and 1
    raw_score_clipped = max(min(raw_score, mx), mn)
    
    if mx == mn:
        risk = 0.5
    else:
        risk = 1 - (raw_score_clipped - mn) / (mx - mn)

    threat_type = _classify_threat(features)

    return {
        "risk_score": float(round(risk, 3)),
        "threat_type": str(threat_type),
        "features": {str(k): float(v) for k, v in zip(FEATURES, features)},
        "flag": bool(risk > 0.50) or (threat_type != "anomaly"),
        "raw_score": float(raw_score),
        "mn": float(mn),
        "mx": float(mx)
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