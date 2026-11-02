import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Multi-Tool API Platform"
    ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    RATE_LIMIT_PER_MINUTE: str = "30/minute"

settings = Settings()
