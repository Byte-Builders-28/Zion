import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from policy.executor import get_enforcement_state

from middleware.interceptor import total_threats, log_queue

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    state = get_enforcement_state()

    ips_blocked = state.get("blocked_ips", 0)
    rate_limited_ips = state.get("rate_limited_ips", 0)
    revoked_tokens_count = state.get("revoked_tokens_count", 0)

    return {
        "ips_blocked": ips_blocked,
        "rate_limited_ips": rate_limited_ips,
        "revoked_tokens_count": revoked_tokens_count,
        "total_threats": total_threats
    }


@router.websocket("/logs")
async def logs_stream(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # send logs if available
            if not log_queue.empty():
                log = log_queue.get()
                await websocket.send_json(log)
            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket Error] {e}")
# router webstcoket? need to send termial logs to display in frontend
