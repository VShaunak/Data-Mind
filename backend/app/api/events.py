import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.engine.events import broadcaster

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/stream/{session_id}")
async def api_event_stream(session_id: str, request: Request):
    queue = broadcaster.subscribe(session_id)

    async def event_generator():
        try:
            while True:
                # Check for client disconnect
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield {
                        "event": "agent_event",
                        "data": json.dumps(event)
                    }
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield {
                        "event": "ping",
                        "data": json.dumps({"type": "ping"})
                    }
        finally:
            broadcaster.unsubscribe(session_id, queue)

    return EventSourceResponse(event_generator())

