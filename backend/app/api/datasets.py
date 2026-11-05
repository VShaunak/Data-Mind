import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.engine.profiling import (
    inspect_dataset_metadata,
    generate_dataset_profile,
    load_dataset,
)
from app.database.models import update_session, get_session

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

@router.post("/upload")
async def api_upload_dataset(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    sheet_name: Optional[str] = Form(None),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    ext = Path(file.filename).suffix.lower()
    allowed_exts = {".csv", ".xlsx", ".xls", ".json", ".parquet", ".sqlite", ".sqlite3", ".db"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Supported: {', '.join(allowed_exts)}"
        )

    # Generate unique stored filename
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    dest_path = settings.datasets_dir / safe_name

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = inspect_dataset_metadata(str(dest_path))
    profile = generate_dataset_profile(str(dest_path), sheet_name=sheet_name)

    if session_id:
        sess = get_session(session_id)
        if sess:
            update_session(
                session_id,
                dataset_path=str(dest_path),
                dataset_name=file.filename,
                dataset_profile=profile
            )

    return {
        "success": True,
        "file_name": file.filename,
        "stored_path": str(dest_path),
        "metadata": metadata,
        "profile": profile
    }

@router.get("/preview")
async def api_preview_dataset(path: str, sheet_name: Optional[str] = None, limit: int = 50):
    try:
        df = load_dataset(path, sheet_name=sheet_name, nrows=min(limit, 200))
        # Serialize NaNs, timestamps, booleans cleanly
        data = df.to_dict(orient="records")
        columns = [{"name": str(col), "type": str(df[col].dtype)} for col in df.columns]
        return {
            "columns": columns,
            "data": data,
            "total_rows": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def api_profile_dataset(path: str, sheet_name: Optional[str] = None):
    try:
        profile = generate_dataset_profile(path, sheet_name=sheet_name)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

