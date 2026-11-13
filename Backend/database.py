import hashlib
import sqlite3

DB_NAME = "aquatrack_v2.db"


def get_connection():
  return sqlite3.connect(DB_NAME)


def hash_password(password: str) -> str:
  return hashlib.sha256(password.encode()).hexdigest()


def init_db():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute(
      """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            daily_goal INTEGER DEFAULT 2000,
            weight_kg REAL DEFAULT 65.0
        )"""
  )
  cursor.execute(
      """CREATE TABLE IF NOT EXISTS consumptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            drink_type TEXT NOT NULL,
            amount_ml INTEGER NOT NULL,
            effective_ml INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )"""
  )
  conn.commit()
  conn.close()