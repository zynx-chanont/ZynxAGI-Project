from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "ZynxAGI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Keys (Optional for now)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Basic Settings
    SECRET_KEY: str = "zynx-agi-secret-key-development"  # This should be overridden in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM Gateway Settings
    ZYNX_LLM_PROVIDER: str = "openai"  # Default provider: "openai", "zynx_local", "claude"
    ZYNX_LOCAL_API_URL: Optional[str] = None
    HMAC_PSEUDONYM_KEY: str = "zynx-pseudonym-key-development"  # Should be overridden in production
    RETENTION_PERIOD_DAYS: int = 90
    CROSS_BORDER_COMPLIANCE: bool = True
    
    # Cultural Intelligence
    CULTURAL_INTELLIGENCE_MODEL: str = "deeja-v1"
    THAI_CULTURAL_WEIGHT: float = 0.8
    DEFAULT_CULTURAL_THRESHOLD: float = 0.7
    FORMAL_CONTEXT_WEIGHT: float = 0.8
    INFORMAL_CONTEXT_WEIGHT: float = 0.6
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://zynxdata.com",
        "https://www.zynxdata.com"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields instead of forbidding

# Create settings instance
settings = Settings() 