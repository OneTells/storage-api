from pydantic import PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSConfig(BaseModel):
    allow_origins: list[str] = []
    allow_methods: list[str] = ['GET']
    allow_headers: list[str] = []
    allow_credentials: bool = False
    allow_origin_regex: str | None = None
    expose_headers: list[str] = []
    max_age: int = 600


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_nested_delimiter="__")

    secret_token: str

    database_dsn: PostgresDsn
    database_pool_size: int = 5

    base_url: str
    cors_config: CORSConfig


settings = Config()  # type: ignore
