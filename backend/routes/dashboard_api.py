import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from policy.executor import get_enforcement_state
import middleware.interceptor as interceptor_module

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    state = get_enforcement_state()

    return {
        "ips_blocked": len(state.get("blocked_ips", [])),
        "rate_limited_ips": len(state.get("rate_limited_ips", [])),
        "revoked_tokens_count": len(state.get("revoked_tokens", [])),
        "total_threats": interceptor_module.total_threats  # ✅ live value
    }


@router.websocket("/logs")
async def logs_stream(websocket: WebSocket):
    await websocket.accept()
    last_sent = 0

    try:
        while True:
            # Snapshot queue without draining it
            items = []
            temp = []
            while not interceptor_module.log_queue.empty():
                item = interceptor_module.log_queue.get()
                items.append(item)
                temp.append(item)
            for item in temp:
                interceptor_module.log_queue.put(item)

            # Only send logs the client hasn't seen yet
            for log in items[last_sent:]:
                await websocket.send_json(log)
            last_sent = len(items)

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket Error] {e}")