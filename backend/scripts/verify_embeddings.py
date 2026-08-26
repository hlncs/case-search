#!/usr/bin/env python3
"""Verify whether document embeddings are populated in PostgreSQL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import psycopg2

from app.config import settings


def quote_ident(name: str) -> str:
    """Safely quote a PostgreSQL identifier."""
    return '"' + name.replace('"', '""') + '"'


def main() -> int:
    """Inspect database tables and embedding/vector columns."""
    try:
        conn = psycopg2.connect(settings.database_url)
    except Exception as exc:
        print(f"Could not connect to PostgreSQL: {exc}")
        return 1

    try:
        with conn:
            with conn.cursor() as cur:
                print(f"Connected to PostgreSQL: {settings.database_url}")

                cur.execute(
                    "select extname, extversion from pg_extension where extname = 'vector'"
                )
                vector_extension = cur.fetchall()
                if vector_extension:
                    print(f"pgvector extension: installed ({vector_extension[0][1]})")
                else:
                    print("pgvector extension: NOT INSTALLED")

                cur.execute(
                    """
                    select table_schema, table_name
                    from information_schema.tables
                    where table_schema not in ('pg_catalog', 'information_schema')
                      and table_type = 'BASE TABLE'
                    order by table_schema, table_name
                    """
                )
                tables = cur.fetchall()

                if not tables:
                    print("Application tables: none found")
                    print("Embeddings populated: NO")
                    return 0

                print("Application tables:")
                for schema, table in tables:
                    cur.execute(
                        f"select count(*) from {quote_ident(schema)}.{quote_ident(table)}"
                    )
                    row_count = cur.fetchone()[0]
                    print(f"  {schema}.{table}: {row_count} rows")

                cur.execute(
                    """
                    select table_schema, table_name, column_name, data_type, udt_name
                    from information_schema.columns
                    where column_name ilike '%embedding%'
                       or column_name ilike '%vector%'
                       or udt_name = 'vector'
                    order by table_schema, table_name, ordinal_position
                    """
                )
                embedding_columns = cur.fetchall()

                if not embedding_columns:
                    print("Embedding/vector columns: none found")
                    print("Embeddings populated: NO")
                    return 0

                print("Embedding/vector columns:")
                populated_any = False
                for schema, table, column, data_type, udt_name in embedding_columns:
                    cur.execute(
                        f"""
                        select
                            count(*) as total_rows,
                            count({quote_ident(column)}) as populated_rows
                        from {quote_ident(schema)}.{quote_ident(table)}
                        """
                    )
                    total_rows, populated_rows = cur.fetchone()
                    populated_any = populated_any or populated_rows > 0
                    print(
                        f"  {schema}.{table}.{column} "
                        f"({data_type}/{udt_name}): {populated_rows}/{total_rows} populated"
                    )

                print(f"Embeddings populated: {'YES' if populated_any else 'NO'}")
                return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())