from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PGMCP_",
        env_file=".env",
        extra="ignore",
    )

    dsn: SecretStr
    pool_min: int = 1
    pool_max: int = 5
    max_rows: int = 1000
    max_bytes: int = 1_000_000
    statement_timeout_ms: int = 5000
    policy_path: str = "policy.yaml"


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
