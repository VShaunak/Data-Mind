import os
import sys
import platform
import shutil
import subprocess
from fastapi import APIRouter
from app.config import settings
from app.engine.sandbox import is_docker_available
from app.providers.manager import provider_manager
from app.database.connection import get_db_path

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

@router.get("")
async def api_get_diagnostics():
    # 1. OS & Runtime Info
    os_info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
    }

    # 2. Storage Permissions
    storage_ok = False
    storage_err = None
    try:
        test_file = settings.cache_dir / ".perm_test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink()
        storage_ok = True
    except Exception as e:
        storage_err = str(e)

    storage_info = {
        "home_path": str(settings.DATA_MIND_HOME),
        "db_path": str(get_db_path()),
        "writable": storage_ok,
        "error": storage_err,
        "free_disk_gb": round(shutil.disk_usage(settings.DATA_MIND_HOME).free / (1024**3), 2)
    }

    # 3. Docker & WSL2
    docker_up, docker_err = is_docker_available()
    wsl_installed = False
    try:
        proc = subprocess.run(["wsl", "-l", "-q"], capture_output=True, text=True, timeout=2)
        wsl_installed = (proc.returncode == 0)
    except Exception:
        pass

    docker_info = {
        "docker_available": docker_up,
        "docker_error": docker_err,
        "wsl2_installed": wsl_installed,
        "sandbox_mode": "Docker Container" if docker_up else "Isolated Subprocess (AST Guarded)"
    }

    # 4. Local LLM Providers Status
    providers_status = await provider_manager.detect_available_providers()

    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "os_info": os_info,
        "storage": storage_info,
        "docker": docker_info,
        "providers": providers_status,
        "default_provider": settings.DEFAULT_PROVIDER,
        "default_model": settings.DEFAULT_MODEL,
        "overall_status": "healthy"
    }

