import os
import psycopg2

sql = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'attention_sessions'
  AND column_name IN ('entry_time','exit_time');
"""

dsn = os.getenv("MIGRATION_DATABASE_URL") or os.getenv("DATABASE_URL")
if not dsn:
    raise SystemExit("Set MIGRATION_DATABASE_URL or DATABASE_URL env var")

with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        for r in cur.fetchall():
            print(f"{r[0]} | {r[1]}")
