import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from app.config import settings
from app.database.models import get_artifacts_for_session

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])

@router.get("/session/{session_id}")
async def api_get_session_artifacts(session_id: str):
    return get_artifacts_for_session(session_id)

@router.get("/download")
async def api_download_artifact(path: str):
    file_path = Path(path).resolve()
    # Ensure file is inside DATAMIND_HOME
    data_home = settings.DATA_MIND_HOME.resolve()
    if not str(file_path).startswith(str(data_home)):
        raise HTTPException(status_code=403, detail="Unauthorized file path access")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact file not found")
    return FileResponse(str(file_path), filename=file_path.name)

