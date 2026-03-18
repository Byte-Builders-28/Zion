from fastapi import APIRouter
from middleware.interceptor import log_buffer
import pandas as pd

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_stats():
    if not log_buffer:
        return {"msg": "no data"}

    df = pd.DataFrame(log_buffer)

    top_ips = df.groupby("ip").size().sort_values(ascending=False).head(5)

    return {
        "total_requests": len(df),
        "top_ips": top_ips.to_dict()
    }


@router.get("/endpoints")
def endpoint_stats():
    if not log_buffer:
        return {"msg": "no data"}

    df = pd.DataFrame(log_buffer)

    endpoints = df.groupby("endpoint").size()

    return {
        "endpoint_usage": endpoints.to_dict()
    }
