from fastapi import APIRouter
from middleware.interceptor import log_queue
import pandas as pd

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def queue_to_list():
    items = []
    temp = []

    while not log_queue.empty():
        item = log_queue.get()
        items.append(item)
        temp.append(item)

    # push back (so data isn't lost)
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
