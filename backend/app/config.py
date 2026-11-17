from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    
    APP_NAME: str = "SPECTRAMARK"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    DATABASE_URL: str = "sqlite:///./spectramark.db"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    
    MAX_UPLOAD_SIZE_MB: int = 25
    MAX_IMAGE_PIXELS: int = 67_108_864  # 8192 x 8192
    
    MAX_WORKER_THREADS: int = 8


settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
