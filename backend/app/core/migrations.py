from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncConnection

MIGRATION_DIR = Path(__file__).resolve().parent.parent / "migrations"


def _split_sql_statements(sql: str) -> list[str]:
    """Split a migration script into executable SQL statements.

    asyncpg prepares each ``execute`` call as one statement. Passing a whole
    SQL file containing multiple semicolon-separated commands therefore fails
    with ``cannot insert multiple commands into a prepared statement``.

    This splitter is deliberately small but quote-aware so semicolons inside
    single/double quoted strings are not treated as statement boundaries.
    PostgreSQL dollar-quoted blocks are also handled for future migrations.
    """
    statements: list[str] = []
    buffer: list[str] = []
    in_single = False
    in_double = False
    dollar_tag: str | None = None
    i = 0

    while i < len(sql):
        char = sql[i]

        if dollar_tag is not None:
            buffer.append(char)
            if sql.startswith(dollar_tag, i):
                for _ in range(len(dollar_tag) - 1):
                    buffer.append(sql[i + 1])
                    i += 1
                dollar_tag = None
            i += 1
            continue

        if not in_double and char == "'":
            buffer.append(char)
            if i + 1 < len(sql) and sql[i + 1] == "'":
                buffer.append(sql[i + 1])
                i += 2
                continue
            in_single = not in_single
            i += 1
            continue

        if not in_single and char == '"':
            in_double = not in_double
            buffer.append(char)
            i += 1
            continue

        if not in_single and not in_double and char == "$":
            end = sql.find("$", i + 1)
            if end != -1:
                candidate = sql[i : end + 1]
                if candidate == "$$" or candidate[1:-1].replace("_", "").isalnum():
                    dollar_tag = candidate
                    buffer.append(candidate)
                    i = end + 1
                    continue

        if not in_single and not in_double and char == ";":
            statement = "".join(buffer).strip()
            if statement:
                statements.append(statement)
            buffer.clear()
            i += 1
            continue

        buffer.append(char)
        i += 1

    statement = "".join(buffer).strip()
    if statement:
        statements.append(statement)

    return statements


async def run_platform_migrations(connection: AsyncConnection) -> None:
    """Apply idempotent platform migrations safely with asyncpg.

    asyncpg does not accept multiple SQL commands in one prepared statement.
    Therefore every semicolon-separated migration command is executed as its
    own driver statement while the surrounding SQLAlchemy transaction remains
    atomic.
    """
    migration = MIGRATION_DIR / "001_platform_completion.sql"
    sql = migration.read_text(encoding="utf-8")

    for statement in _split_sql_statements(sql):
        await connection.exec_driver_sql(statement)
