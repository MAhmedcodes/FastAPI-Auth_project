from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    #Database 
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    #JWT Auth
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    #Redis / Celery
    REDIS_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_RESULT_BACKEND: str = "redis://localhost:6379/1"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    #Email / SMTP
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 465
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""

    #google oauth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # GitHub OAuth
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str = "http://localhost:8000/auth/github/callback"

    SESSION_SECRET_KEY: str
    class Config:
        env_file = ".env"
        # extra = "ignore"   # don't crash on unknown .env keys


settings = Settings()  # type: ignore
