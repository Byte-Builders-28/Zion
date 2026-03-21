import time
import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse
from queue import Queue
from threading import Lock

from ml.detector import score_request
from policy.smolify_client import generate_policy
from policy.executor import execute_action, is_blocked, is_rate_limited, is_token_revoked, is_endpoint_under_attack
from blockchain.algorand_logger import log_incident

log_queue = Queue(maxsize=10000)
_last_alert_by_key = {}
_alert_lock = Lock()

# Thread-safe counter
total_threats = 0
threat_lock = Lock()


def background_threat_handler(score_result: dict, log_data: dict):
    threat_type = score_result.get("threat_type")
    endpoint = log_data.get("endpoint")
    ip = log_data.get("ip")
    token = log_data.get("token")

    # Throttle by *context* (not globally), so different attack types can trigger
    # their distinct mitigations without being blocked by an unrelated event.
    if threat_type == "token_replay" and token:
        throttle_key = ("token_replay", token)
        throttle_window_s = 2
    elif threat_type == "ddos" and endpoint:
        throttle_key = ("ddos", endpoint)
        throttle_window_s = 5
    else:
        throttle_key = (str(threat_type), str(ip))
        throttle_window_s = 5

    now = time.time()
    with _alert_lock:
        last = _last_alert_by_key.get(throttle_key, 0)
        if now - last < throttle_window_s:
            return
        _last_alert_by_key[throttle_key] = now

    try:
        policy = generate_policy({
            "threat_type": threat_type,
            "endpoint": endpoint,
            "ip": ip,
            "risk_score": score_result.get("risk_score")
        })

        print(policy)

        execute_action(policy.get("action", "monitor"), {
            "ip": ip,
            "token": token,
            "endpoint": endpoint,
            "risk": score_result.get("risk_score", 0.0)
        })

        log_incident({
            "id": str(int(time.time() * 1000)),
            "type": threat_type,
            "endpoint": endpoint,
            "ip": ip,
            "risk": score_result.get("risk_score"),
            "policy": policy.get("rule_name", "unknown")
        })

        print(f"[Threat Handler] Action: {policy.get('action')} | IP: {ip}")

    except Exception as e:
        print(f"[Threat Handler Error] {e}")


def add_log(data: dict):
    try:
        log_queue.put_nowait(data)
    except:
        log_queue.get()
        log_queue.put_nowait(data)


async def interceptor(request: Request, call_next):
    global total_threats

    start_time = time.time()

    # Support for proxies
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(
        "Bearer ")[-1] if "Bearer " in auth_header else ""

    # ── Enforcement gate — runs BEFORE processing request ──
    endpoint_path = request.url.path

    if is_blocked(ip):
        return JSONResponse(status_code=403, content={"detail": "IP blocked by Zion security policy"})

    if is_rate_limited(ip):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded — try again later"})

    if token and is_token_revoked(token):
        return JSONResponse(status_code=401, content={"detail": "Token revoked by Zion security policy"})

    if is_endpoint_under_attack(endpoint_path):
        print(f"[Interceptor] BLOCKED request to {endpoint_path} (Endpoint under attack)")

        # Still log, and (for token-bearing requests) still score, so we can
        # detect token replay and revoke the token even while the endpoint is protected.
        log_data = {
            "endpoint": endpoint_path,
            "method": request.method,
            "ip": ip,
            "timestamp": time.time(),
            "latency": 0.0,
            "token": token,
            "payload_size": int(request.headers.get("content-length", 0)),
            "status_code": 503,
        }

        try:
            if token:
                score_result = score_request(log_data)
                log_data["score_result"] = score_result

                if score_result.get("flag") and score_result.get("threat_type") == "token_replay":
                    asyncio.create_task(
                        asyncio.to_thread(background_threat_handler, score_result, log_data)
                    )
            else:
                log_data["score_result"] = {
                    "risk_score": 0.0,
                    "threat_type": "normal",
                    "features": {},
                    "flag": False,
                }
        except Exception as e:
            log_data["score_result"] = {"flag": False, "error": str(e)}

        add_log(log_data)
        return JSONResponse(
            status_code=503,
            content={"detail": "Service currently under heavy load — dropping traffic"},
        )

    # ── Normal request flow ──
    response = await call_next(request)
    process_time = time.time() - start_time

    payload_size = int(request.headers.get("content-length", 0))

    log_data = {
        "endpoint": endpoint_path,
        "method": request.method,
        "ip": ip,
        "timestamp": time.time(),
        "latency": process_time,
        "token": token,
        "payload_size": payload_size,
        "status_code": response.status_code
    }

    try:

        route = request.scope.get("route")
        tags = getattr(route, "tags", []) if route else []

        if (endpoint_path in {"/docs", "/openapi.json", "/redoc"} or "Dashboard" in tags):
            score_result = {
                "risk_score": 0.0,
                "threat_type": "normal",
                "features": {},
                "flag": False,
            }
        else:

            score_result = score_request(log_data)

        log_data["score_result"] = score_result

        print(
            f"[Interceptor] Score: {score_result.get('risk_score')} | "
            f"Flag: {score_result.get('flag')} | "
            f"Type: {score_result.get('threat_type')}"
        )

        if score_result.get("flag"):
            # thread-safe increment
            with threat_lock:
                total_threats += 1

            asyncio.create_task(
                asyncio.to_thread(background_threat_handler,
                                  score_result, log_data)
            )

    except Exception as e:
        print(f"[Interceptor Error] Threat scoring failed: {e}")
        log_data["score_result"] = {"flag": False, "error": str(e)}

    add_log(log_data)
    return response


def get_batch(max_items=100):
    batch = []
    while not log_queue.empty() and len(batch) < max_items:
        batch.append(log_queue.get())
    return batch
