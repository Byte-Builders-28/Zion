import time
from fastapi import Request
from queue import Queue
from ml.detector import score_request
from policy.smolify_client import generate_policy
from blockchain.algorand_logger import log_incident

log_queue = Queue(maxsize=10000)  # prevent memory overflow


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
        
        # If threat exists, generate policy and log
        if score_result.get("flag"):
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
        print(f"[Interceptor Error] Threat scoring failed: {e}")
        log_data["score_result"] = {"flag": False, "error": str(e)}

    add_log(log_data)

    return response


def get_batch(max_items=100):
    batch = []

    while not log_queue.empty() and len(batch) < max_items:
        batch.append(log_queue.get())

    return batch
