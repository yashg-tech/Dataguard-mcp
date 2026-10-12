from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from mcp.shared.context import LifespanContextT
from mcp.types import RequestParams
from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from pg_analyst_mcp.config import get_settings
from pg_analyst_mcp.db.pool import make_pool


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Create shared database resources for the MCP server's lifetime."""
    pool = make_pool(get_settings())

    try:
        yield {"pool": pool}
    finally:
        pool.close()


mcp = FastMCP("pg-analyst", lifespan=app_lifespan)


@mcp.tool()
def ping() -> str:
    """Health check. Returns 'pong'. Use it to confirm the server is reachable."""
    return "pong"


@mcp.tool()
def list_tables(
    ctx: Context[ServerSession, LifespanContextT, RequestParams],
    schema: str = "public",
) -> list[dict[str, str]]:
    """List tables visible to the configured database role in a schema."""
    lifespan_context = cast(
        dict[str, Any],
        ctx.request_context.lifespan_context,
    )
    pool = cast(ConnectionPool, lifespan_context["pool"])

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY table_name
                """,
                (schema,),
            )
            rows = cur.fetchall()

    return [
        {"table_name": str(table_name), "table_type": str(table_type)}
        for table_name, table_type in rows
    ]


@mcp.tool()
def describe_table(
    ctx: Context[ServerSession, LifespanContextT, RequestParams],
    table_name: str,
    schema: str = "public",
) -> list[dict[str, str | bool]]:
    """Describe accessible columns of a table, including data types and nullability."""
    lifespan_context = cast(
        dict[str, Any],
        ctx.request_context.lifespan_context,
    )
    pool = cast(ConnectionPool, lifespan_context["pool"])

    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.ordinal_position
                FROM information_schema.columns AS c
                JOIN information_schema.tables AS t
                  ON t.table_schema = c.table_schema
                 AND t.table_name = c.table_name
                WHERE c.table_schema = %s
                  AND c.table_name = %s
                  AND t.table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY c.ordinal_position
                """,
                (schema, table_name),
            )
            rows = cur.fetchall()

    return [
        {
            "column_name": str(column_name),
            "data_type": str(data_type),
            "is_nullable": str(is_nullable) == "YES",
        }
        for column_name, data_type, is_nullable, _ in rows
    ]


@mcp.tool()
def sample_rows(
    ctx: Context[ServerSession, LifespanContextT, RequestParams],
    table_name: str,
    schema: str = "public",
) -> list[dict[str, Any]]:
    """Return at most 10 sample rows from a table using SELECT-permitted columns."""
    lifespan_context = cast(
        dict[str, Any],
        ctx.request_context.lifespan_context,
    )
    pool = cast(ConnectionPool, lifespan_context["pool"])

    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Find columns on which the current database role has SELECT permission.
            cur.execute(
                """
                SELECT c.column_name
                FROM information_schema.columns AS c
                JOIN information_schema.tables AS t
                  ON t.table_schema = c.table_schema
                 AND t.table_name = c.table_name
                WHERE c.table_schema = %s
                  AND c.table_name = %s
                  AND t.table_type IN ('BASE TABLE', 'VIEW')
                  AND has_column_privilege(
                    current_user,
                    c.table_schema || '.' || c.table_name,
                    c.column_name,
                    'SELECT'
                )
                ORDER BY c.ordinal_position
                """,
                (schema, table_name),
            )
            columns = [str(row["column_name"]) for row in cur.fetchall()]

            # No accessible columns means there is no data to return.
            if not columns:
                return []

            # Identifiers are safely composed; the row limit is fixed at 10.
            query = sql.SQL("SELECT {} FROM {}.{} LIMIT 10").format(
                sql.SQL(", ").join(sql.Identifier(column) for column in columns),
                sql.Identifier(schema),
                sql.Identifier(table_name),
            )
            cur.execute(query)
            rows = cur.fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    mcp.run()
