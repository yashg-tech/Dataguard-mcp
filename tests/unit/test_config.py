from pydantic import SecretStr

from pg_analyst_mcp.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(dsn="postgresql://user:password@localhost:5433/analytics")

    assert settings.pool_min == 1
    assert settings.pool_max == 5
    assert settings.max_rows == 1000
    assert settings.max_bytes == 1_000_000
    assert settings.statement_timeout_ms == 5000


def test_dsn_uses_secret_str() -> None:
    settings = Settings(dsn="postgresql://user:password@localhost:5433/analytics")

    assert isinstance(settings.dsn, SecretStr)
    assert "**********" in repr(settings.dsn)
    assert "password" not in repr(settings.dsn)
