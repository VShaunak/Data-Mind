import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from app.database.models import log_event

class EventBroadcaster:
    """
    Manages Server-Sent Events (SSE) streaming for real-time agent execution progress.
    Supports multi-subscriber broadcasting and session event caching.
    """
    def __init__(self):
        # session_id -> list of asyncio.Queue
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        # session_id -> list of past events (for replay on reconnect)
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def subscribe(self, session_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        if session_id not in self._subscribers:
            self._subscribers[session_id] = []
        self._subscribers[session_id].append(q)

        # Replay past events if any
        if session_id in self._history:
            for event in self._history[session_id]:
                q.put_nowait(event)

        return q

    def unsubscribe(self, session_id: str, q: asyncio.Queue) -> None:
        if session_id in self._subscribers:
            if q in self._subscribers[session_id]:
                self._subscribers[session_id].remove(q)
            if not self._subscribers[session_id]:
                del self._subscribers[session_id]

    async def broadcast(
        self,
        session_id: str,
        task_id: Optional[str],
        stage: str,
        status: str,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = {
            "session_id": session_id,
            "task_id": task_id,
            "stage": stage,
            "status": status,
            "message": message or "",
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        }

        # Cache in memory
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(event)

        # Persist to database
        try:
            log_event(
                session_id=session_id,
                task_id=task_id,
                stage=stage,
                status=status,
                message=message,
                metadata=metadata,
            )
        except Exception:
            pass

        # Dispatch to active queues
        if session_id in self._subscribers:
            for q in list(self._subscribers[session_id]):
                try:
                    q.put_nowait(event)
                except Exception:
                    pass

broadcaster = EventBroadcaster()

