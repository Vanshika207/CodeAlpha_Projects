"""
database.py
------------
Handles all SQLite database operations for the AI Smart Language Translator.
Responsible for creating the database/table, saving translation records,
fetching history, and clearing history.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database connection and translation history operations."""

    def __init__(self, db_name: str = "translation_history.db"):
        # Store the database in the same folder as the application
        self.db_path = Path(__file__).resolve().parent / db_name
        self._create_table()

    def _get_connection(self):
        """Create and return a new SQLite connection."""
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        """Create the translations table if it does not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_translation(self, original_text: str, translated_text: str,
                          source_lang: str, target_lang: str) -> None:
        """Insert a new translation record into the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO translations
                    (original_text, translated_text, source_lang, target_lang, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (original_text, translated_text, source_lang, target_lang, timestamp),
            )
            conn.commit()

    def get_history(self, limit: int = 100):
        """Retrieve translation history, most recent first."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, original_text, translated_text, source_lang, target_lang, timestamp
                FROM translations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cursor.fetchall()

    def clear_history(self) -> None:
        """Delete all translation history records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translations")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='translations'")
            conn.commit()

    def delete_entry(self, entry_id: int) -> None:
        """Delete a single history entry by its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translations WHERE id = ?", (entry_id,))
            conn.commit()
