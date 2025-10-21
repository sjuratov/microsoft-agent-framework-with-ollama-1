"""API-specific configuration settings."""

import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIConfig(BaseSettings):
    """API configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # CORS settings
    cors_origins: str = Field(
        default="*",  # Allow all origins (development only)
        description="Comma-separated list of allowed CORS origins, or '*' to allow all",
    )

    # Timeout settings (in seconds)
    generation_timeout: int = Field(
        default=600,
        ge=60,
        le=1800,
        description="Maximum time for slogan generation (seconds)",
    )
    request_timeout: int = Field(
        default=630,
        ge=60,
        le=1800,
        description="Overall HTTP request timeout (seconds)",
    )

    # Logging settings
    log_level: str = Field(
        default="WARNING",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Concurrency settings
    max_concurrent_requests: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent generation requests",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def configure_logging(self) -> None:
        """Configure logging based on settings."""
        log_level = getattr(logging, self.log_level.upper(), logging.WARNING)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Set specific loggers
        logging.getLogger("uvicorn").setLevel(log_level)
        logging.getLogger("fastapi").setLevel(log_level)
        logging.getLogger("src.api").setLevel(log_level)


# Singleton instance
_api_config: APIConfig | None = None


def get_api_config() -> APIConfig:
    """Get or create the API configuration singleton."""
    global _api_config
    if _api_config is None:
        _api_config = APIConfig()
        _api_config.configure_logging()
    return _api_config
