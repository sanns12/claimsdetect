"""
Database module - SQLite with aiosqlite
"""

import aiosqlite
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "app", "core", "insurance.db")

_db: Optional[aiosqlite.Connection] = None


async def init_db() -> None:
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row  # lets you access columns by name
    await _create_tables()
    print(f"✅ SQLite connected at {DB_PATH}")


async def _create_tables() -> None:
    await _db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_number TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            patient_name TEXT,
            hospital_name TEXT,
            age INTEGER,
            disease TEXT,
            admission_date TEXT,
            discharge_date TEXT,
            duration_days INTEGER,
            claim_amount REAL,
            status TEXT DEFAULT 'Submitted',
            risk_score REAL,
            fraud_probability REAL,
            lime_explanation TEXT,
            mismatch_flag INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS claim_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            filename TEXT,
            file_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (claim_id) REFERENCES claims(id)
        );

        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            status TEXT,
            changed_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (claim_id) REFERENCES claims(id)
        );

        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            trust_status TEXT DEFAULT 'green',
            fraud_percentage REAL DEFAULT 0,
            total_claims INTEGER DEFAULT 0,
            flagged_claims INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    await _db.commit()


async def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db


async def get_users_collection() -> aiosqlite.Connection:
    return await get_db()


async def get_claims_collection() -> aiosqlite.Connection:
    return await get_db()


async def get_claim_files_collection() -> aiosqlite.Connection:
    return await get_db()


async def get_status_history_collection() -> aiosqlite.Connection:
    return await get_db()


async def get_companies_collection() -> aiosqlite.Connection:
    return await get_db()


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None
        print("🛑 SQLite connection closed")