from typing import Any

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def copy_database(source: str, target: str, db_settings: dict[str, Any]) -> None:
    """Copy a database using the source as a template.

    Args:
        source: The template database.
        target: The target database to be created.
        db_settings: Database connection settings.
    """
    run_sql(f'DROP DATABASE IF EXISTS "{target}"', db_settings)
    run_sql(
        f'CREATE DATABASE "{target}" WITH TEMPLATE "{source}"',
        db_settings,
    )


def delete_database(database: str, db_settings: dict[str, Any]) -> None:
    """Delete a database if it exists.

    Args:
        database: The database to be deleted.
        db_settings: Database connection settings.
    """
    run_sql(f'DROP DATABASE IF EXISTS "{database}"', db_settings)


def run_sql(sql: str, db_settings: dict[str, Any]) -> None:
    """Run the SQL query on PostgreSQL  bypassing the Django ORM.

    Args:
        sql: The query to be ran.
        db_settings: A dict of database connection settings.
    """
    conn = psycopg2.connect(
        host=db_settings["HOST"],
        port=db_settings["PORT"],
        user=db_settings["USER"],
        password=db_settings["PASSWORD"],
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql)
    conn.close()
