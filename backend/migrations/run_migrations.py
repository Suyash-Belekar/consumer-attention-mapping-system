"""Simple migration runner for SQL files in backend/migrations

Usage:
  - Set environment variable `MIGRATION_DATABASE_URL` or `DATABASE_URL` to a full Postgres DSN.
  - Run: python backend/migrations/run_migrations.py

Behavior:
  - Creates a table `migration_versions(filename TEXT PRIMARY KEY, applied_at TIMESTAMPTZ)`
  - Applies all `*.sql` files in this directory in lexicographic order that are not yet applied.
  - Each applied file is recorded to avoid re-applying.

This is intentionally minimal; for production use prefer Alembic.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
import argparse

import psycopg2
from psycopg2.extras import execute_values

MIGRATIONS_DIR = Path(__file__).parent

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS migration_versions (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL
);
"""


def get_db_url() -> str:
    return os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")


def list_sql_files() -> list[Path]:
    return sorted(p for p in MIGRATIONS_DIR.iterdir() if p.suffix.lower() == ".sql")


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(TABLE_SQL)
    conn.commit()


def already_applied(conn, filename: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM migration_versions WHERE filename = %s", (filename,))
        return cur.fetchone() is not None


def mark_applied(conn, filename: str):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO migration_versions (filename, applied_at) VALUES (%s, NOW()) ON CONFLICT (filename) DO NOTHING",
            (filename,),
        )
    conn.commit()


def apply_file(conn, path: Path):
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def run(dry_run: bool = False):
    db_url = get_db_url()
    if not db_url:
        print("Error: set MIGRATION_DATABASE_URL or DATABASE_URL env var with a Postgres DSN")
        sys.exit(2)

    files = list_sql_files()
    if not files:
        print("No .sql migrations found in", MIGRATIONS_DIR)
        return

    conn = psycopg2.connect(dsn=db_url)
    try:
        ensure_table(conn)

        pending = [p for p in files if not already_applied(conn, p.name)]

        if not pending:
            print("No pending migrations; database is up to date.")
            return

        print(f"Pending migrations: {[p.name for p in pending]}")
        if dry_run:
            print("Dry run: no changes will be applied.")
            return

        for p in pending:
            print(f"Applying {p.name}...")
            try:
                apply_file(conn, p)
                mark_applied(conn, p.name)
                print(f"Applied {p.name}")
            except Exception:
                conn.rollback()
                print(f"Failed to apply {p.name}")
                raise

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SQL migrations from backend/migrations")
    parser.add_argument("--dry-run", action="store_true", help="List pending migrations without applying")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
