from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid
from datetime import datetime
from app.database.models import (
    SessionModel,
    TaskModel,
    create_session,
    list_sessions,
    get_session,
    delete_session,
    get_tasks_for_session,
    get_artifacts_for_session,
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "Untitled Analysis"
    selected_provider: Optional[str] = None
    selected_model: Optional[str] = None

@router.post("", response_model=SessionModel)
async def api_create_session(req: CreateSessionRequest):
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()
    session = SessionModel(
        id=session_id,
        title=req.title or "Untitled Analysis",
        created_at=now,
        updated_at=now,
        selected_provider=req.selected_provider,
        selected_model=req.selected_model,
        status="idle",
    )
    create_session(session)
    return session

@router.get("", response_model=List[SessionModel])
async def api_list_sessions():
    return list_sessions()

@router.get("/{session_id}")
async def api_get_session_detail(session_id: str):
    sess = get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    tasks = get_tasks_for_session(session_id)
    artifacts = get_artifacts_for_session(session_id)
    return {
        "session": sess,
        "tasks": tasks,
        "artifacts": artifacts
    }

@router.delete("/{session_id}")
async def api_delete_session(session_id: str):
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or already deleted")
    return {"success": True, "message": "Session deleted"}

