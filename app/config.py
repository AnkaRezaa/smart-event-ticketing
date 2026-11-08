import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR
    APP_NAME: str = "Smart Event Ticketing System"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "super-secret-key-at-least-32-chars-long-protection"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/storage/smart_ticketing.db"

    # Storage paths
    PRIVATE_FACES_DIR: str = str(BASE_DIR / "storage" / "private_faces")
    FEATURES_DIR: str = str(BASE_DIR / "storage" / "features")
    MODEL_ARTIFACTS_DIR: str = str(BASE_DIR / "storage" / "model_artifacts")

    # Security
    SESSION_COOKIE_NAME: str = "smart_ticket_session"
    SESSION_MAX_AGE_SECONDS: int = 86400  # 24 hours
    SECURE_COOKIE: bool = False
    CSRF_SECRET: str = "csrf-secret-key-32-chars-minimum-token-protection"

    # Computer Vision / HOG Configuration
    HOG_ORIENTATIONS: int = 9
    HOG_PIXELS_PER_CELL: int = 8
    HOG_CELLS_PER_BLOCK: int = 2
    HOG_BLOCK_NORM: str = "L2-Hys"
    TARGET_FACE_SIZE: int = 128

    # ML parameters
    KNN_DEFAULT_K: int = 3
    RECOGNITION_THRESHOLD: float = 0.68
    PSO_NUM_PARTICLES: int = 15
    PSO_MAX_ITERATIONS: int = 20

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.PRIVATE_FACES_DIR, exist_ok=True)
os.makedirs(settings.FEATURES_DIR, exist_ok=True)
os.makedirs(settings.MODEL_ARTIFACTS_DIR, exist_ok=True)

