from fastapi import APIRouter
import requests

from attack.scenarios import rate_abuse, credential_stuffing, token_replay, param_fuzzing, endpoint_scrape
# (last two run function is main())

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/ddos")
def spam_attack(target: str = "http://127.0.0.1:8000/test"):

    rate_abuse.run_simulation(url=target)
    return {"msg": "executed"}


@router.post("/credit")
def spam_attack(target: str = "http://127.0.0.1:8000/test"):

    credential_stuffing.run_simulation(url=target)
    return {"msg": "executed"}


@router.post("/token")
def spam_attack(target: str = "http://127.0.0.1:8000/test"):

    token_replay.run_simulation(url=target)
    return {"msg": "executed"}


@router.post("/param")
def spam_attack():

    param_fuzzing.main()
    return {"msg": "executed"}


@router.post("/endpoint")
def spam_attack():

    endpoint_scrape.main()
    return {"msg": "executed"}
