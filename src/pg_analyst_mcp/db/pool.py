from psycopg_pool import ConnectionPool

from pg_analyst_mcp.config import Settings


def make_pool(settings: Settings) -> ConnectionPool:
    pool = ConnectionPool(
        conninfo=settings.dsn.get_secret_value(),
        min_size=settings.pool_min,
        max_size=settings.pool_max,
        open=True,
    )

    try:
        pool.wait(timeout=10)
    except Exception:
        pool.close()
        raise

    return pool
