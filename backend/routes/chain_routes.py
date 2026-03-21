from fastapi import APIRouter
from uuid import uuid4

from ml.detector import score_request
from blockchain.algorand_logger import get_chain_history, log_incident_async

router = APIRouter()


@router.post("/api/analyze")
def analyze_request(payload: dict):
    """Scores request and writes incident to chain in background when flagged."""
    score = score_request(payload)

    if score.get("flag"):
        incident = {
            "id": payload.get("id") or f"SG-{uuid4().hex[:8]}",
            "type": score.get("threat_type", "anomaly"),
            "endpoint": payload.get("endpoint", "unknown"),
            "ip": payload.get("ip", "0.0.0.0"),
            "risk": score.get("risk_score", 0.0),
            "policy": payload.get("policy", "auto")
        }
        log_incident_async(incident)

    return score


@router.get("/api/chain")
def get_chain_log(limit: int = 20):
    """Returns last N on-chain incident records."""
    return get_chain_history(limit)


@router.get("/api/chain/{tx_id}")
def get_tx_detail(tx_id: str):
    from algosdk.v2client import algod
    client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
    try:
        tx = client.pending_transaction_info(tx_id)
        return {"tx_id": tx_id, "data": tx, "found": True}
    except Exception:
        return {"tx_id": tx_id, "found": False}
    