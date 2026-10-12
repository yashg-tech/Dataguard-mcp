import os

import psycopg
import pytest


@pytest.fixture
def ro_conn() -> psycopg.Connection:
    return psycopg.connect(
        host=os.getenv("MCP_DB_HOST", "localhost"),
        port=os.getenv("MCP_DB_PORT", "5433"),
        dbname=os.getenv("MCP_DB_NAME", "analytics"),
        user=os.getenv("MCP_DB_USER", "mcp_ro"),
        password=os.getenv("MCP_DB_PASSWORD", "DataGuardMcp123"),
    )


@pytest.mark.integration
def test_ro_role_allows_safe_select(ro_conn: psycopg.Connection) -> None:
    with ro_conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT order_id, customer_id, order_date, category, amount
            FROM big_orders
            LIMIT 5
            """
        )

        rows = cursor.fetchall()

    assert len(rows) <= 5


BAD_SQL = [
    "DELETE FROM big_orders",
    "UPDATE big_orders SET amount = 0",
    "CREATE TABLE test_blocked (id INT)",
    "SELECT customer_email FROM big_orders LIMIT 1",
]


@pytest.mark.integration
@pytest.mark.parametrize("sql", BAD_SQL)
def test_ro_role_refuses(
    ro_conn: psycopg.Connection,
    sql: str,
) -> None:
    with pytest.raises(psycopg.Error):
        with ro_conn.cursor() as cursor:
            cursor.execute(sql)
