from functools import lru_cache

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "MyGO Band Manager"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    secret_key: str = "change-me-before-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = Field(
        default="mysql+pymysql://root:password@127.0.0.1:3306/mygo_band?charset=utf8mb4"
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    admin_email: str = "admin@mygoband.com"
    admin_username: str = "MyGO Admin"
    admin_password: str = "MyGO-Admin-9F3vP8!"
    admin_band_position: str = "guitar"

    ai_base_url: str = ""
    ai_model: str = ""
    ai_api_key: str = ""
    ai_timeout_seconds: int = 45
    enable_ai_proxy: bool = False

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
