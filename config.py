from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    ACCESS_TOKEN_EXPIRE_DAYS: int = 1


    BACKEND_CORS_ORIGINS : list[str] = ["http://127.0.0.1:8000"]
    MONGO_DB_USERNAME: str
    MONGO_DB_PASSWORD: str
    JWT_SECRET: str
    JWT_ALG: str

    model_config = SettingsConfigDict(env_file=".env")

    
settings = Settings()