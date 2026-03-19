import time
from fastapi import Request, BackgroundTasks
import asyncio
from queue import Queue
from ml.detector import score_request
from policy.smolify_client import generate_policy
from blockchain.algorand_logger import log_incident

log_queue = Queue(maxsize=10000)  # prevent memory overflow

last_alert_time = 0

def background_threat_handler(score_result: dict, log_data: dict):
    global last_alert_time
    # Only send to blockchain once every 10 seconds to avoid spamming the testnet API
    if time.time() - last_alert_time < 10:
        return
    last_alert_time = time.time()
    
    try:
        policy = generate_policy({
            "threat_type": score_result.get("threat_type"),
            "endpoint": log_data["endpoint"],
            "ip": log_data["ip"],
            "risk_score": score_result.get("risk_score")
        })
        log_incident({
            "id": str(int(time.time()*1000)),
            "type": score_result.get("threat_type"),
            "endpoint": log_data["endpoint"],
            "ip": log_data["ip"],
            "risk": score_result.get("risk_score"),
            "policy": policy.get("rule_name", "unknown")
        })
    except Exception as e:
        print(f"[Threat Handler Error] {e}")

def add_log(data: dict):
    try:
        log_queue.put_nowait(data)
    except:
        # queue full → drop oldest
        log_queue.get()
        log_queue.put_nowait(data)


async def interceptor(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split("Bearer ")[-1] if "Bearer " in auth_header else ""
    
    payload_size = int(request.headers.get("content-length", 0))

    log_data = {
        "endpoint": request.url.path,
        "method": request.method,
        "ip": request.client.host if request.client else "unknown",
        "timestamp": time.time(),
        "latency": process_time,
        "token": token,
        "payload_size": payload_size,
        "status_code": response.status_code
    }
    
    try:
        score_result = score_request(log_data)
        log_data["score_result"] = score_result
        print(f"[Interceptor] Score: {score_result['risk_score']} | Flag: {score_result['flag']} | Type: {score_result['threat_type']}")
        
        # If threat exists, generate policy and log
        if score_result.get("flag"):
            # run the slow blockchain logging in background so it doesn't block the request
            asyncio.create_task(asyncio.to_thread(background_threat_handler, score_result, log_data))
            
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
