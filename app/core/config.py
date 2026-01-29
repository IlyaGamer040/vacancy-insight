from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv
from typing import List

class Settings(BaseSettings):
    load_dotenv()

    # Database
    DATABASE_URL: str = getenv("DATABASE_URL")

    # Security
    SECRET_KEY: str = getenv("SECRET_KEY")
    ALGORITHM: str = getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MIN: int = getenv("ACCESS_TOKEN_EXPIRE_MIN")
    
    # Application
    DEBUG: bool = False
    PROJECT_NAME: str = getenv("PROJECT_NAME", "VacancyInsight")
    API_V1_PREFIX: str = getenv("API_V1_PREFIX", "/api/v1")

    # CORS
    CORS_ORIGINS: List[str] = getenv("CORS_ORIGINS", ["*"])

    # External APIs
    HH_API_URL: str = getenv("HH_API_URL", "https://api.hh.ru")
    SUPERJOB_API_KEY: str = getenv("SUPERJOB_API_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()