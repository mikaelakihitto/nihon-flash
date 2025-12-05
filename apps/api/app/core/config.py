from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/nihon_flash"
    JWT_SECRET: str = "changeme"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
