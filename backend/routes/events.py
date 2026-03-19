from fastapi import APIRouter
from middleware.interceptor import log_queue
import pandas as pd

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/run-detection")
def run_detection():
    if not log_queue:
        return {"msg": "no data"}

    df = pd.DataFrame(log_queue)

    counts = df.groupby("ip").size()

    suspicious = counts[counts > 20]

    return {
        "flagged_ips": suspicious.index.tolist(),
        "counts": suspicious.to_dict()
    }


@router.post("/clear-logs")
def clear_logs():
    log_queue.clear()
    return {"msg": "logs cleared"}
