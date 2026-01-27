from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL = "sq;ote+aiosqlite:///./database.db"

    PROJECT_NAME: str = "VacancyInsight"
    API_v1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()