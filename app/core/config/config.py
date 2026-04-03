from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"
        # extra = "ignore"   # don't crash on unknown .env keys


settings = Settings()  # type: ignore