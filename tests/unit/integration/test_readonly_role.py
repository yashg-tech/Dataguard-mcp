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
def test_schema_metadata_hides_restricted_column(
    ro_conn: psycopg.Connection,
) -> None:
    with ro_conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'big_orders'
            """
        )
        column_names = {row[0] for row in cursor.fetchall()}

    assert "order_id" in column_names
    assert "amount" in column_names
    assert "customer_email" not in column_names
