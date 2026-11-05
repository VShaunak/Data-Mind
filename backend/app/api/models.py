from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.config import settings
from app.providers.manager import provider_manager

router = APIRouter(prefix="/api/models", tags=["models"])

class TestConnectionRequest(BaseModel):
    provider: str
    model: str

class UpdateConfigRequest(BaseModel):
    provider: str
    base_url: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None

@router.get("/providers")
async def api_get_providers():
    """Detect local providers and fetch available models."""
    status = await provider_manager.detect_available_providers()
    return {
        "providers": status,
        "default_provider": settings.DEFAULT_PROVIDER,
        "default_model": settings.DEFAULT_MODEL,
        "temperature": settings.TEMPERATURE,
        "top_p": settings.TOP_P,
        "max_tokens": settings.MAX_TOKENS,
    }

@router.post("/test")
async def api_test_connection(req: TestConnectionRequest):
    provider = provider_manager.get_provider(req.provider)
    res = await provider.test_connection(req.model)
    return res

@router.post("/config")
async def api_update_config(req: UpdateConfigRequest):
    provider_manager.update_provider_url(req.provider, req.base_url)
    if req.model:
        settings.DEFAULT_MODEL = req.model
    if req.temperature is not None:
        settings.TEMPERATURE = req.temperature
    if req.top_p is not None:
        settings.TOP_P = req.top_p
    if req.max_tokens is not None:
        settings.MAX_TOKENS = req.max_tokens
    settings.DEFAULT_PROVIDER = req.provider

    return {
        "success": True,
        "message": f"Updated settings for {req.provider}",
        "default_provider": settings.DEFAULT_PROVIDER,
        "default_model": settings.DEFAULT_MODEL,
    }

