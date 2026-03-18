from fastapi import APIRouter
import requests

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/spam")
def spam_attack(target: str = "http://127.0.0.1:8000/test"):
    for _ in range(50):
        try:
            requests.get(target)
        except:
            pass

    return {"msg": "spam executed"}
