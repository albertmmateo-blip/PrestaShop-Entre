"""Configuration settings for the Loyalty API."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Application
    app_name: str = "Loyalty API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 3000

    # Database
    database_url: str

    # Security
    api_key_salt: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100

    # CORS
    cors_origins: List[str] = ["http://localhost:8001", "http://localhost:3000"]
    cors_allow_credentials: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Business Rules
    earn_rate: float = 0.015
    points_multiplier: int = 10000
    expiration_months: int = 3

    # External Services
    email_provider: str = ""
    email_api_key: str = ""
    whatsapp_provider: str = ""
    whatsapp_api_key: str = ""

    # Monitoring
    sentry_dsn: str = ""


settings = Settings()
