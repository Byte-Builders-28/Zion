from fastapi import APIRouter
from middleware.interceptor import log_buffer
import pandas as pd

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("/")
def get_anomalies():
    if not log_buffer:
        return {"msg": "no data"}

    df = pd.DataFrame(log_buffer)

    counts = df.groupby("ip").size()
    suspicious = counts[counts > 20]

    return suspicious.to_dict()
