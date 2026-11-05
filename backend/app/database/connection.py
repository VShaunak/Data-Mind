import sqlite3
import json
from pathlib import Path
from typing import Generator
from app.config import settings

def get_db_path() -> Path:
    return settings.db_path

_db_initialized = False

def _create_raw_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(get_db_path()), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory enabled."""
    global _db_initialized
    if not _db_initialized:
        init_db()
    return _create_raw_connection()

def init_db() -> None:
    """Initialize SQLite database tables and indexes."""
    global _db_initialized
    _db_initialized = True
    settings.init_storage()
    conn = _create_raw_connection()
    try:
        with conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                dataset_path TEXT,
                dataset_name TEXT,
                dataset_profile TEXT,
                selected_provider TEXT,
                selected_model TEXT,
                status TEXT DEFAULT 'idle'
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                plan TEXT,
                code TEXT,
                error_message TEXT,
                traceback TEXT,
                attempt_count INTEGER DEFAULT 1,
                stdout TEXT,
                stderr TEXT,
                chart_json TEXT,
                report_json TEXT,
                duration_seconds REAL DEFAULT 0.0,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                task_id TEXT,
                artifact_type TEXT NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS execution_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                task_id TEXT,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                metadata TEXT,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_session ON tasks(session_id);
            CREATE INDEX IF NOT EXISTS idx_artifacts_session ON artifacts(session_id);
            CREATE INDEX IF NOT EXISTS idx_events_session_task ON execution_events(session_id, task_id);
            """)
    finally:
        conn.close()
