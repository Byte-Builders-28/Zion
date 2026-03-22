from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from attack.scenarios import rate_abuse, credential_stuffing, token_replay, param_fuzzing, endpoint_scrape
# (last two run function is main())

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/ddos")
async def simulate_ddos(target: str = "http://127.0.0.1:8000/test"):
    await rate_abuse.run_simulation(url=target, type="ddos")
    return {"msg": "executed"}

@router.post("/rate_flood")
async def simulate_rate_flood(target: str = "http://127.0.0.1:8000/test"):
    await rate_abuse.run_simulation(url=target, type="rate_flood")
    return {"msg": "executed"}


@router.post("/credit")
async def simulate_credential_stuffing(target: str = "http://127.0.0.1:8000/login"):
    # credential_stuffing uses requests + time.sleep (sync), so run it off the event loop.
    await run_in_threadpool(credential_stuffing.run_simulation, url=target)
    return {"msg": "executed"}


@router.post("/token")
async def simulate_token_replay(target: str = "http://127.0.0.1:8000/test"):
    await token_replay.run_simulation(url=target)
    return {"msg": "executed"}


@router.post("/param")
async def simulate_param_fuzzing(base: str = "http://127.0.0.1:8000"):
    # param_fuzzing.main() parses CLI args; call run() directly instead.
    await run_in_threadpool(
        param_fuzzing.run,
        base=base,
        total_requests=350,
        mutations=12,
        concurrency=24,
        spoofed_ip="198.51.100.20",
        timeout_s=2.5,
    )
    return {"msg": "executed"}


@router.post("/endpoint")
async def simulate_endpoint_scrape(base: str = "http://127.0.0.1:8000"):
    # endpoint_scrape.main() parses CLI args; call run() directly instead.
    await run_in_threadpool(
        endpoint_scrape.run,
        base=base,
        total_requests=250,
        unique_endpoints=50,
        concurrency=16,
        spoofed_ip="198.51.100.10",
        timeout_s=2.5,
    )
    return {"msg": "executed"}
