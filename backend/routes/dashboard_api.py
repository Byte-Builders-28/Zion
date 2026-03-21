from fastapi import APIRouter
from middleware.interceptor import log_queue
from blockchain.algorand_logger import log_incident_async
from ml.detector import score_request
import pandas as pd

from policy.executor import get_enforcement_state\

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

incident_counter = 1


def queue_to_list():
    items = []
    temp = []
    while not log_queue.empty():
        item = log_queue.get()
        items.append(item)
        temp.append(item)
    for item in temp:
        log_queue.put(item)
    return items


@router.get("/stats")
def get_stats():
    logs = queue_to_list()
    if not logs:
        return {"msg": "no data"}
    df = pd.DataFrame(logs)
    top_ips = df.groupby("ip").size().sort_values(ascending=False).head(5)
    return {
        "total_requests": len(df),
        "top_ips": top_ips.to_dict()
    }


@router.get("/endpoints")
def endpoint_stats():
    logs = queue_to_list()
    if not logs:
        return {"msg": "no data"}
    df = pd.DataFrame(logs)
    endpoints = df.groupby("endpoint").size()
    return {
        "endpoint_usage": endpoints.to_dict()
    }


@router.get("/raw_logs")
def get_raw_logs():
    return queue_to_list()


@router.post("/analyze")
async def analyze(req: dict):
    global incident_counter

    # Step 1 — ML scores the request
    result = score_request(req)

    # Step 2 — threat flagged → log to Algorand + Appwrite
    if result.get("flag"):
        log_incident_async({
            "id":       f"SG-{incident_counter:03d}",
            "type":     result.get("threat_type"),
            "endpoint": req.get("endpoint", "/"),
            "ip":       req.get("ip", "0.0.0.0"),
            "risk":     result.get("risk_score"),
            "policy":   "auto_flagged"
        })
        incident_counter += 1

    return result



@router.get("/enforcement")
def get_enforcement():
    """Returns currently blocked IPs, rate limited IPs, revoked tokens."""
    return get_enforcement_state()