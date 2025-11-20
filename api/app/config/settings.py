from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

"""
This module defines the application's configuration settings using environment variables and default values.
"""


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # ========================================
    # API Configuration
    # ========================================
    PROJECT_NAME: str = "Analytics Gateway"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    BASE_URL: str
    ENVIRONMENT: str = "dev"
    
    # ========================================
    # CORS
    # ========================================
    BACKEND_CORS_ORIGINS: str | List[str] = "*"
    
    # Méthodes HTTP autorisées
    ALLOWED_METHODS: List[str] = ["GET"]
    
    # Headers autorisés
    ALLOWED_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "X-OAuth-Credentials",
        "X-Property-ID",
        "Accept",
    ]
    
    # ========================================
    # Validators
    # ========================================
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list"""
        if v is None or v == "":
            return ["*"]
        
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        if isinstance(v, list):
            return v
        
        return ["*"]
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valider l'environnement"""
        allowed = ["dev", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    # ========================================
    # Pydantic Config
    # ========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields in .env
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Créer et cache l'instance de settings (singleton pattern).
    Utiliser cette fonction dans les dependencies FastAPI.
    """
    return Settings()

# Instance globale pour import direct
settings = get_settings()
