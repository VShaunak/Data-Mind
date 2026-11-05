import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import init_db
from app.api.sessions import router as sessions_router
from app.api.datasets import router as datasets_router
from app.api.analysis import router as analysis_router
from app.api.events import router as events_router
from app.api.models import router as models_router
from app.api.artifacts import router as artifacts_router
from app.api.diagnostics import router as diagnostics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and storage directories on startup
    init_db()
    yield
    # Shutdown cleanup if needed

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Data Mind: Autonomous AI Data Analyst & Coding Agent",
    lifespan=lifespan,
)

# Enable CORS for Vite and desktop frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Register API routers
app.include_router(sessions_router)
app.include_router(datasets_router)
app.include_router(analysis_router)
app.include_router(events_router)
app.include_router(models_router)
app.include_router(artifacts_router)
app.include_router(diagnostics_router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "tagline": settings.TAGLINE
    }

@app.post("/api/shutdown")
async def shutdown_app():
    """Cleanly exit and kill the application backend."""
    import threading
    import time
    def _kill():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=_kill, daemon=True).start()
    return {"success": True, "message": "Data Mind backend shutting down"}

# Mount compiled production frontend if exists (must be mounted after all API routes)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
