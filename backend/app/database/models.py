from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import json
from datetime import datetime
from app.database.connection import get_db_connection

class SessionModel(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    dataset_path: Optional[str] = None
    dataset_name: Optional[str] = None
    dataset_profile: Optional[Dict[str, Any]] = None
    selected_provider: Optional[str] = None
    selected_model: Optional[str] = None
    status: str = "idle"

class TaskModel(BaseModel):
    id: str
    session_id: str
    prompt: str
    created_at: str
    completed_at: Optional[str] = None
    status: str
    plan: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    attempt_count: int = 1
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    chart_json: Optional[Dict[str, Any]] = None
    report_json: Optional[Dict[str, Any]] = None
    duration_seconds: float = 0.0

class ArtifactModel(BaseModel):
    id: str
    session_id: str
    task_id: Optional[str] = None
    artifact_type: str
    name: str
    file_path: str
    content: Optional[str] = None
    created_at: str

class ExecutionEventModel(BaseModel):
    id: Optional[int] = None
    session_id: str
    task_id: Optional[str] = None
    stage: str
    status: str
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

# Helper Database CRUD Operations
def create_session(session: SessionModel) -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, dataset_path, dataset_name, dataset_profile, selected_provider, selected_model, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.title,
                    session.created_at,
                    session.updated_at,
                    session.dataset_path,
                    session.dataset_name,
                    json.dumps(session.dataset_profile) if session.dataset_profile else None,
                    session.selected_provider,
                    session.selected_model,
                    session.status
                )
            )
    finally:
        conn.close()

def get_session(session_id: str) -> Optional[SessionModel]:
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return None
        return SessionModel(
            id=row["id"],
            title=row["title"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            dataset_path=row["dataset_path"],
            dataset_name=row["dataset_name"],
            dataset_profile=json.loads(row["dataset_profile"]) if row["dataset_profile"] else None,
            selected_provider=row["selected_provider"],
            selected_model=row["selected_model"],
            status=row["status"]
        )
    finally:
        conn.close()

def list_sessions() -> List[SessionModel]:
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
        result = []
        for row in rows:
            result.append(
                SessionModel(
                    id=row["id"],
                    title=row["title"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    dataset_path=row["dataset_path"],
                    dataset_name=row["dataset_name"],
                    dataset_profile=json.loads(row["dataset_profile"]) if row["dataset_profile"] else None,
                    selected_provider=row["selected_provider"],
                    selected_model=row["selected_model"],
                    status=row["status"]
                )
            )
        return result
    finally:
        conn.close()

def update_session(session_id: str, **kwargs) -> None:
    conn = get_db_connection()
    try:
        kwargs["updated_at"] = datetime.now().isoformat()
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            if k == "dataset_profile" and isinstance(v, dict):
                values.append(json.dumps(v))
            else:
                values.append(v)
        values.append(session_id)
        with conn:
            conn.execute(f"UPDATE sessions SET {', '.join(fields)} WHERE id = ?", values)
    finally:
        conn.close()

def delete_session(session_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cur.rowcount > 0
    finally:
        conn.close()

def create_task(task: TaskModel) -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO tasks (id, session_id, prompt, created_at, completed_at, status, plan, code, error_message, traceback, attempt_count, stdout, stderr, chart_json, report_json, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.session_id,
                    task.prompt,
                    task.created_at,
                    task.completed_at,
                    task.status,
                    json.dumps(task.plan) if task.plan else None,
                    task.code,
                    task.error_message,
                    task.traceback,
                    task.attempt_count,
                    task.stdout,
                    task.stderr,
                    json.dumps(task.chart_json) if task.chart_json else None,
                    json.dumps(task.report_json) if task.report_json else None,
                    task.duration_seconds
                )
            )
    finally:
        conn.close()

def update_task(task_id: str, **kwargs) -> None:
    conn = get_db_connection()
    try:
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            if k in ("plan", "chart_json", "report_json") and isinstance(v, (dict, list)):
                values.append(json.dumps(v))
            else:
                values.append(v)
        values.append(task_id)
        with conn:
            conn.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?", values)
    finally:
        conn.close()

def get_tasks_for_session(session_id: str) -> List[TaskModel]:
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at ASC", (session_id,)).fetchall()
        result = []
        for row in rows:
            result.append(
                TaskModel(
                    id=row["id"],
                    session_id=row["session_id"],
                    prompt=row["prompt"],
                    created_at=row["created_at"],
                    completed_at=row["completed_at"],
                    status=row["status"],
                    plan=json.loads(row["plan"]) if row["plan"] else None,
                    code=row["code"],
                    error_message=row["error_message"],
                    traceback=row["traceback"],
                    attempt_count=row["attempt_count"],
                    stdout=row["stdout"],
                    stderr=row["stderr"],
                    chart_json=json.loads(row["chart_json"]) if row["chart_json"] else None,
                    report_json=json.loads(row["report_json"]) if row["report_json"] else None,
                    duration_seconds=row["duration_seconds"] or 0.0
                )
            )
        return result
    finally:
        conn.close()

def log_event(session_id: str, task_id: Optional[str], stage: str, status: str, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO execution_events (session_id, task_id, stage, status, message, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    task_id,
                    stage,
                    status,
                    message,
                    json.dumps(metadata) if metadata else None,
                    datetime.now().isoformat()
                )
            )
    finally:
        conn.close()

def get_events_for_task(task_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM execution_events WHERE task_id = ? ORDER BY id ASC", (task_id,)).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "task_id": r["task_id"],
                "stage": r["stage"],
                "status": r["status"],
                "message": r["message"],
                "metadata": json.loads(r["metadata"]) if r["metadata"] else None,
                "timestamp": r["timestamp"]
            }
            for r in rows
        ]
    finally:
        conn.close()

def save_artifact(artifact: ArtifactModel) -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO artifacts (id, session_id, task_id, artifact_type, name, file_path, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id,
                    artifact.session_id,
                    artifact.task_id,
                    artifact.artifact_type,
                    artifact.name,
                    artifact.file_path,
                    artifact.content,
                    artifact.created_at
                )
            )
    finally:
        conn.close()

def get_artifacts_for_session(session_id: str) -> List[ArtifactModel]:
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * FROM artifacts WHERE session_id = ? ORDER BY created_at DESC", (session_id,)).fetchall()
        return [
            ArtifactModel(
                id=r["id"],
                session_id=r["session_id"],
                task_id=r["task_id"],
                artifact_type=r["artifact_type"],
                name=r["name"],
                file_path=r["file_path"],
                content=r["content"],
                created_at=r["created_at"]
            )
            for r in rows
        ]
    finally:
        conn.close()

