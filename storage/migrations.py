# storage/migrations.py
"""
Simple migration system for SQLite database.
"""

import sqlite3
from pathlib import Path


CURRENT_SCHEMA_VERSION = 1


def get_migration_scripts() -> dict:
    """
    Returns migration scripts keyed by version.
    Each version is a list of SQL statements.
    """
    return {
        1: [
            # Initial schema (from schema.sql)
            # In practice, read schema.sql and execute it
        ]
    }


def init_database(db_path: Path) -> None:
    """
    Initialize the database with the current schema.
    
    Args:
        db_path: Path to SQLite database file
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor.executescript(schema_sql)
    
    # Ensure schema_version table exists and has current version
    cursor.execute("""
        INSERT OR IGNORE INTO schema_version (version)
        VALUES (?)
    """, (CURRENT_SCHEMA_VERSION,))
    
    conn.commit()
    conn.close()


def get_schema_version(db_path: Path) -> int:
    """Get the current schema version from database."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_version")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0
    except sqlite3.OperationalError:
        return 0


def migrate_database(db_path: Path) -> None:
    """
    Run pending migrations.
    
    Args:
        db_path: Path to SQLite database file
    """
    current_version = get_schema_version(db_path)
    
    if current_version >= CURRENT_SCHEMA_VERSION:
        return  # Already up to date
    
    # For now, just init if needed
    if current_version == 0:
        init_database(db_path)
