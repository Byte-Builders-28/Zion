import time
from fastapi import Request
from queue import Queue

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

    log_data = {
        "endpoint": request.url.path,
        "method": request.method,
        "ip": request.client.host if request.client else "unknown",
        "timestamp": time.time(),
        "latency": process_time,
    }

    add_log(log_data)

    return response


def get_batch(max_items=100):
    batch = []

    while not log_queue.empty() and len(batch) < max_items:
        batch.append(log_queue.get())

    return batch
