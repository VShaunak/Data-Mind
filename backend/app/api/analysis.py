import uuid
import re
from pathlib import Path
import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.config import settings
from app.database.models import (
    get_session,
    update_session,
    create_task,
    update_task,
    get_tasks_for_session,
    TaskModel,
)
from app.engine.langgraph_agent import agent_executor

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

class StartAnalysisRequest(BaseModel):
    session_id: str
    prompt: str
    dataset_path: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None

# Active asyncio tasks: task_id -> asyncio.Task
_running_tasks: Dict[str, asyncio.Task] = {}
# Session active task lookup: session_id -> task_id
_session_active_tasks: Dict[str, str] = {}

class CancelAnalysisRequest(BaseModel):
    session_id: str
    task_id: Optional[str] = None

async def _run_agent_task(task_id: str, initial_state: Dict[str, Any]):
    session_id = initial_state.get("session_id")
    try:
        await agent_executor.ainvoke(initial_state)
    except asyncio.CancelledError:
        from app.engine.events import broadcaster
        await broadcaster.broadcast(
            session_id=session_id,
            task_id=task_id,
            stage="CANCELLED",
            status="failed",
            message="Task was killed/cancelled by user.",
            metadata={"cancelled": True}
        )
        try:
            update_task(
                task_id=task_id,
                status="cancelled",
                error_message="Task was stopped by user.",
            )
            update_session(session_id, status="idle")
        except Exception:
            pass
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        from app.engine.events import broadcaster
        await broadcaster.broadcast(
            session_id=session_id,
            task_id=task_id,
            stage="FAILED",
            status="failed",
            message=f"Execution error: {str(e)}",
            metadata={"traceback": tb}
        )
        try:
            update_task(
                task_id=task_id,
                status="failed",
                error_message=str(e),
                traceback=tb
            )
            update_session(session_id, status="idle")
        except Exception:
            pass
    finally:
        _running_tasks.pop(task_id, None)
        if _session_active_tasks.get(session_id) == task_id:
            _session_active_tasks.pop(session_id, None)

@router.post("/cancel")
async def api_cancel_analysis(req: CancelAnalysisRequest):
    """Cancel and terminate an active analysis task."""
    task_id = req.task_id or _session_active_tasks.get(req.session_id)
    if task_id and task_id in _running_tasks:
        running_task = _running_tasks[task_id]
        running_task.cancel()
        _running_tasks.pop(task_id, None)
        _session_active_tasks.pop(req.session_id, None)

        from app.engine.events import broadcaster
        await broadcaster.broadcast(
            session_id=req.session_id,
            task_id=task_id,
            stage="CANCELLED",
            status="failed",
            message="Task killed by user.",
            metadata={"cancelled": True}
        )
        update_task(
            task_id=task_id,
            status="cancelled",
            error_message="Task killed by user."
        )
        update_session(req.session_id, status="idle")
        return {"success": True, "message": "Task killed successfully."}

    # If no task actively executing in memory, reset session to idle
    update_session(req.session_id, status="idle")
    return {"success": True, "message": "Session reset to idle."}

@router.post("/start")
async def api_start_analysis(req: StartAnalysisRequest):
    sess = get_session(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    ds_path = req.dataset_path or sess.dataset_path
    if not ds_path and req.prompt:
        raw_paths = re.findall(r'([a-zA-Z]:\\[^\r\n"\'<>]+)', req.prompt)
        for cand in raw_paths:
            cand_clean = cand.strip().rstrip('.,;')
            p = Path(cand_clean)
            if p.is_file():
                ds_path = str(p)
                break
            elif p.is_dir():
                prompt_lower = req.prompt.lower()
                matched_csv = None
                for f in p.glob('*.csv'):
                    if f.stem.lower() in prompt_lower:
                        matched_csv = str(f)
                        break
                if not matched_csv:
                    first_csv = next(p.glob('*.csv'), None)
                    if first_csv:
                        matched_csv = str(first_csv)
                if matched_csv:
                    ds_path = matched_csv
                    break

        if ds_path:
            p_obj = Path(ds_path)
            from app.engine.profiling import generate_dataset_profile
            try:
                prof = generate_dataset_profile(ds_path)
                update_session(req.session_id, dataset_path=ds_path, dataset_name=p_obj.name, dataset_profile=prof)
            except Exception:
                update_session(req.session_id, dataset_path=ds_path, dataset_name=p_obj.name)

    if not ds_path:
        raise HTTPException(status_code=400, detail="No dataset attached to this session. Please upload a dataset first or provide a dataset path.")

    task_id = f"task_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()

    # Create task record in SQLite
    task = TaskModel(
        id=task_id,
        session_id=req.session_id,
        prompt=req.prompt,
        created_at=now,
        status="running",
        attempt_count=1,
    )
    create_task(task)

    selected_provider = req.provider or sess.selected_provider or settings.DEFAULT_PROVIDER
    selected_model = req.model or sess.selected_model or settings.DEFAULT_MODEL

    # Retrieve prior completed task code from this session for iterative refinement
    prior_tasks = get_tasks_for_session(req.session_id)
    prior_code = None
    for pt in reversed(prior_tasks):
        if pt.code and pt.status == "completed":
            prior_code = pt.code
            break

    # Update session status
    update_session(
        req.session_id,
        status="running",
        selected_provider=selected_provider,
        selected_model=selected_model
    )

    initial_state = {
        "session_id": req.session_id,
        "task_id": task_id,
        "user_prompt": req.prompt,
        "dataset_path": ds_path,
        "dataset_profile": sess.dataset_profile or {},
        "analysis_plan": {},
        "current_code": "",
        "previous_code": prior_code,
        "error_message": None,
        "traceback": None,
        "attempt_count": 1,
        "selected_provider": selected_provider,
        "selected_model": selected_model,
        "execution_stdout": "",
        "execution_stderr": "",
        "chart_json": None,
        "metrics_json": None,
        "analytical_report": "",
        "final_status": "running",
        "duration_seconds": 0.0,
    }

    # Launch tracking task in background
    running_task = asyncio.create_task(_run_agent_task(task_id, initial_state))
    _running_tasks[task_id] = running_task
    _session_active_tasks[req.session_id] = task_id

    return {
        "success": True,
        "task_id": task_id,
        "session_id": req.session_id,
        "status": "running"
    }

