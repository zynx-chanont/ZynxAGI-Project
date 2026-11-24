import json
import os
from typing import Any, List, Optional, Union

from pydantic import Field, field_validator, model_validator

# Simple BaseSettings replacement for when pydantic-settings is not available
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    HAS_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel as BaseSettings  # type: ignore
    SettingsConfigDict = dict  # type: ignore
    HAS_PYDANTIC_SETTINGS = False


DEFAULT_ALLOWED_ORIGINS: List[str] = [
    "https://zynx-agi.netlify.app",
    "https://zynxdata.com",
    "https://www.zynxdata.com",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]


def parse_allowed_origins(value: Any) -> List[str]:
    """Parse ALLOWED_ORIGINS from a list, JSON array string, or comma-separated string."""
    if value is None:
        return list(DEFAULT_ALLOWED_ORIGINS)

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return list(DEFAULT_ALLOWED_ORIGINS)
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if not isinstance(parsed, list):
                raise ValueError("ALLOWED_ORIGINS JSON value must be a list of origins")
            items = [str(item).strip() for item in parsed]
        else:
            items = [item.strip() for item in stripped.split(",")]
    elif isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value]
    else:
        raise ValueError("ALLOWED_ORIGINS must be a list or comma-separated string")

    cleaned: List[str] = []
    for origin in items:
        normalized = origin.rstrip("/")
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


class Settings(BaseSettings):
    if HAS_PYDANTIC_SETTINGS:
        model_config = SettingsConfigDict(
            env_file=".env",
            case_sensitive=True,
            extra="ignore",
        )

    # Application Settings
    APP_NAME: str = "ZynxAGI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Unified AI Provider Settings (preferred)
    AI_PROVIDER: Optional[str] = None
    AI_API_KEY: Optional[str] = None
    AI_MODEL: Optional[str] = None
    AI_REQUEST_TIMEOUT: float = 20.0

    # Provider-specific API Keys & Defaults (backend environment variables only)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-latest"
    ANTHROPIC_MAX_TOKENS: int = 1000
    ANTHROPIC_TEMPERATURE: float = 0.7

    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_MODEL: str = "gemini-2.5-flash"

    # Security Settings
    SECRET_KEY: str = "zynx-agi-secret-key-development"  # Override in production via env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    STORAGE_ENCRYPTION_KEY: Optional[str] = None
    ZYNX_INTERNAL_SERVICE_TOKEN: Optional[str] = None

    # Cultural Intelligence
    CULTURAL_INTELLIGENCE_MODEL: str = "deeja-v1"
    THAI_CULTURAL_WEIGHT: float = 0.8
    DEFAULT_CULTURAL_THRESHOLD: float = 0.7
    FORMAL_CONTEXT_WEIGHT: float = 0.8
    INFORMAL_CONTEXT_WEIGHT: float = 0.6

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: list(DEFAULT_ALLOWED_ORIGINS)
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _normalize_allowed_origins(cls, value: Any) -> List[str]:
        return parse_allowed_origins(value)

    @model_validator(mode="after")
    def _validate_security_and_cors(self) -> "Settings":
        # CORS validation
        origins = parse_allowed_origins(self.ALLOWED_ORIGINS)
        if not self.DEBUG and "*" in origins:
            raise ValueError(
                "Wildcard '*' is not permitted in ALLOWED_ORIGINS when DEBUG=False"
            )
        self.ALLOWED_ORIGINS = origins

        # Insecure fallback validation when DEBUG=False
        insecure_fallbacks = {
            "zynx-agi-secret-key-development",
            "your-secret-key",
            "your-super-secret-key-change-in-production",
            "secret",
            "changeme",
        }
        if not self.DEBUG:
            if not self.SECRET_KEY or self.SECRET_KEY.strip() in insecure_fallbacks:
                raise ValueError(
                    "SECRET_KEY must be overridden with a secure production secret when DEBUG=False"
                )

        # STORAGE_ENCRYPTION_KEY format validation
        if self.STORAGE_ENCRYPTION_KEY:
            import base64
            try:
                dec = base64.urlsafe_b64decode(self.STORAGE_ENCRYPTION_KEY.encode())
                if len(dec) != 32:
                    raise ValueError("STORAGE_ENCRYPTION_KEY must decode to exactly 32 bytes")
            except Exception as exc:
                raise ValueError(
                    f"STORAGE_ENCRYPTION_KEY must be 32 url-safe base64-encoded bytes: {exc}"
                )

        return self

    @property
    def ai(self) -> "Settings":
        """Compatibility accessor for legacy clients referencing settings.ai."""
        return self


def load_settings() -> Settings:
    """Load Settings from environment variables (supports fallback when pydantic-settings is absent)."""
    if HAS_PYDANTIC_SETTINGS:
        return Settings()
    kwargs: dict[str, Any] = {}
    for field_name in Settings.model_fields:
        if field_name in os.environ:
            kwargs[field_name] = os.environ[field_name]
    return Settings(**kwargs)


# Create settings instance
settings = load_settings()
