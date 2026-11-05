import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Data Mind"
    APP_VERSION: str = "1.0.0"
    TAGLINE: str = "Think Data. Discover Intelligence."

    # Windows user data directory
    # Default to %APPDATA%\DataMind on Windows, or ~/.datamind
    DATA_MIND_HOME: Path = Path(os.environ.get(
        "DATAMIND_HOME",
        os.path.join(os.environ.get("APPDATA", str(Path.home())), "DataMind")
    ))

    # Backend server host and port
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Default LLM Provider & Model settings
    DEFAULT_PROVIDER: str = "ollama"  # ollama | lm_studio | llamacpp | openai_compatible
    DEFAULT_MODEL: str = "llama3:8b"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    LM_STUDIO_BASE_URL: str = "http://127.0.0.1:1234/v1"
    LLAMACPP_BASE_URL: str = "http://127.0.0.1:8080/v1"
    GENERIC_OPENAI_BASE_URL: str = "http://127.0.0.1:8000/v1"
    
    TEMPERATURE: float = 0.1
    TOP_P: float = 0.95
    MAX_TOKENS: int = 4096
    CONTEXT_WINDOW: int = 8192
    LLM_TIMEOUT: int = 120

    # Execution & Sandbox settings
    MAX_CORRECTION_RETRIES: int = 3
    SANDBOX_TIMEOUT_SECONDS: int = 60
    SANDBOX_MEMORY_LIMIT: str = "1g"
    SANDBOX_CPU_LIMIT: float = 2.0
    DOCKER_IMAGE_NAME: str = "datamind-sandbox:latest"
    FORCE_DOCKER_SANDBOX: bool = False

    # Chunking and profiling limits
    MAX_PREVIEW_ROWS: int = 100
    MAX_PROFILE_ROWS: int = 50000
    PROFILE_SAMPLE_SIZE: int = 3

    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def database_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "database"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return self.database_dir / "datamind.db"

    @property
    def config_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "config"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def datasets_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "datasets"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def sessions_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "sessions"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def artifacts_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "artifacts"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def charts_dir(self) -> Path:
        p = self.artifacts_dir / "charts"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def reports_dir(self) -> Path:
        p = self.artifacts_dir / "reports"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def code_dir(self) -> Path:
        p = self.artifacts_dir / "code"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def exports_dir(self) -> Path:
        p = self.artifacts_dir / "exports"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def logs_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def cache_dir(self) -> Path:
        p = self.DATA_MIND_HOME / "cache"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def init_storage(self) -> None:
        """Create all required directory paths on startup."""
        _ = self.database_dir
        _ = self.config_dir
        _ = self.datasets_dir
        _ = self.sessions_dir
        _ = self.artifacts_dir
        _ = self.charts_dir
        _ = self.reports_dir
        _ = self.code_dir
        _ = self.exports_dir
        _ = self.logs_dir
        _ = self.cache_dir

settings = Settings()

