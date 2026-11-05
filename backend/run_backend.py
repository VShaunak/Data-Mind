import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, log_level="info")

