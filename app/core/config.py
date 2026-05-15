from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_env: str

    database_url: str

    access_token_secret: str
    refresh_token_secret: str
    jwt_algorithm: str

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    redis_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()