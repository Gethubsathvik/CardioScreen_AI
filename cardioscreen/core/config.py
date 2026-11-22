"""Core configuration using Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import __version__


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "CardioScreen AI"
    app_version: str = __version__
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Paths
    root_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")
    models_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "models")
    reports_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "reports")
    static_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "static")

    # Data
    data_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data" / "heart.csv")
    model_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "models" / "heart_model.joblib")
    random_state: int = 42
    test_size: float = 0.2
    target_col: str = "target"
    target_one_means_healthy: bool = True

    # Risk bands
    risk_bands: list[tuple[float, str]] = [(0.33, "low"), (0.66, "moderate"), (1.01, "high")]

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: list[str] = ["*"]

    # Model
    model_threshold: float = 0.5
    max_batch_size: int = 1000

    # Disclaimer
    disclaimer: str = (
        "Educational research project. Not a medical device and not a substitute for "
        "professional medical advice, diagnosis or treatment."
    )

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Security (future)
    api_key_enabled: bool = False
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100
    rate_limit_window: int = 60


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

# Backward compatibility exports
ROOT = settings.root_dir
DATA_PATH = settings.data_path
MODELS_DIR = settings.models_dir
REPORTS_DIR = settings.reports_dir
MODEL_PATH = settings.model_path
RANDOM_STATE = settings.random_state
TEST_SIZE = settings.test_size
TARGET_COL = settings.target_col
TARGET_ONE_MEANS_HEALTHY = settings.target_one_means_healthy
RISK_BANDS = tuple(settings.risk_bands)
DISCLAIMER = settings.disclaimer