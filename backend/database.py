"""
Database Module for Insurance Claims API
Using SQLite with simple connection pooling
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import threading

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "insurance.db")

# Thread-local storage for connections
thread_local = threading.local()

def get_db():
    """Get a database connection for the current thread"""
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect(DATABASE_PATH)
        thread_local.connection.row_factory = sqlite3.Row
    return thread_local.connection

def close_db():
    """Close the database connection for the current thread"""
    if hasattr(thread_local, "connection"):
        thread_local.connection.close()
        del thread_local.connection

def init_db():
    """Initialize database tables with your schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 1️⃣ USERS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'hospital', 'insurance')),
            created_at TIMESTAMP NOT NULL
        )
    ''')
    
    # 2️⃣ COMPANIES table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('hospital', 'corporate')),
            trust_status TEXT NOT NULL CHECK(trust_status IN ('green', 'yellow', 'black')) DEFAULT 'green',
            fraud_percentage REAL DEFAULT 0,
            total_claims INTEGER DEFAULT 0,
            flagged_claims INTEGER DEFAULT 0,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    
    # 3️⃣ CLAIMS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER,
            patient_name TEXT,
            hospital_name TEXT,
            age INTEGER NOT NULL,
            disease TEXT NOT NULL,
            admission_date DATE NOT NULL,
            discharge_date DATE NOT NULL,
            duration_days INTEGER,
            claim_amount REAL NOT NULL,
            risk_score REAL,
            fraud_probability REAL,
            status TEXT NOT NULL CHECK(status IN ('Submitted', 'AI Processing', 'Manual Review', 'Approved', 'Flagged', 'Fraud')),
            lime_explanation TEXT,
            mismatch_flag BOOLEAN DEFAULT 0,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
        )
    ''')
    
    # 4️⃣ CLAIM_FILES table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claim_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_url TEXT NOT NULL,
            file_type TEXT NOT NULL,
            extracted_text TEXT,
            uploaded_at TIMESTAMP NOT NULL,
            FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
        )
    ''')
    
    # 5️⃣ CLAIM_STATUS_HISTORY table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claim_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            old_status TEXT NOT NULL,
            new_status TEXT NOT NULL,
            changed_by INTEGER NOT NULL,
            changed_at TIMESTAMP NOT NULL,
            FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE,
            FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_user_id ON claims(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_company_id ON claims(company_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_claim_files_claim_id ON claim_files(claim_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status_history_claim_id ON claim_status_history(claim_id)')
    
    conn.commit()
    print("✅ Database initialized with your schema")

def seed_database():
    """Seed database with initial data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if users exist
    cursor.execute("SELECT COUNT(*) as count FROM users")
    row = cursor.fetchone()
    user_count = row[0] if row else 0
    
    if user_count == 0:
        # Insert sample users
        import bcrypt
        
        # Create password hash for 'password123'
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw('password123'.encode('utf-8'), salt).decode('utf-8')
        now = datetime.now().isoformat()
        
        users = [
            ('John Doe', 'user@example.com', password_hash, 'user', now),
            ('City Hospital', 'hospital@example.com', password_hash, 'hospital', now),
            ('Insurance Admin', 'insurance@example.com', password_hash, 'insurance', now)
        ]
        
        cursor.executemany('''
            INSERT INTO users (full_name, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', users)
        
        print("✅ Sample users added")
    
    # Check if companies exist
    cursor.execute("SELECT COUNT(*) as count FROM companies")
    row = cursor.fetchone()
    company_count = row[0] if row else 0
    
    if company_count == 0:
        now = datetime.now().isoformat()
        companies = [
            ('City General Hospital', 'hospital', 'green', 0.5, 450, 8, now),
            ('MediCare Plus Clinic', 'hospital', 'green', 0.9, 320, 12, now),
            ('HealthFirst Medical', 'hospital', 'yellow', 1.8, 280, 18, now),
            ('QuickCare Emergency', 'hospital', 'yellow', 2.1, 195, 15, now),
            ('Premier Health Group', 'hospital', 'green', 0.8, 520, 14, now)
        ]
        
        cursor.executemany('''
            INSERT INTO companies (name, type, trust_status, fraud_percentage, total_claims, flagged_claims, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', companies)
        
        print("✅ Sample companies added")
    
    conn.commit()
    print("✅ Database seeding complete")

# Collection wrapper classes for compatibility
class SQLiteCollection:
    def __init__(self, table_name):
        self.table_name = table_name
    
    def find_one(self, query):
        conn = get_db()
        cursor = conn.cursor()
        
        conditions = []
        values = []
        for key, value in query.items():
            if key == '_id':
                conditions.append("id = ?")
                values.append(value)
            else:
                conditions.append(f"{key} = ?")
                values.append(value)
        
        sql = f"SELECT * FROM {self.table_name} WHERE {' AND '.join(conditions)}"
        cursor.execute(sql, values)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def find(self, query=None, limit=50):
        conn = get_db()
        cursor = conn.cursor()
        
        sql = f"SELECT * FROM {self.table_name}"
        params = []
        
        if query:
            conditions = []
            for key, value in query.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY id DESC"
        if limit:
            sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def insert_one(self, data):
        conn = get_db()
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()
        
        class Result:
            def __init__(self, id):
                self.inserted_id = id
        
        return Result(cursor.lastrowid)
    
    def update_one(self, filter, update):
        conn = get_db()
        cursor = conn.cursor()
        
        set_items = []
        values = []
        for key, value in update.get('$set', {}).items():
            set_items.append(f"{key} = ?")
            values.append(value)
        
        where_items = []
        for key, value in filter.items():
            where_items.append(f"{key} = ?")
            values.append(value)
        
        sql = f"UPDATE {self.table_name} SET {', '.join(set_items)} WHERE {' AND '.join(where_items)}"
        cursor.execute(sql, values)
        conn.commit()
        
        class Result:
            def __init__(self, count):
                self.modified_count = count
        
        return Result(cursor.rowcount)
    
    def delete_one(self, filter):
        conn = get_db()
        cursor = conn.cursor()
        
        where_items = []
        values = []
        for key, value in filter.items():
            where_items.append(f"{key} = ?")
            values.append(value)
        
        sql = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_items)}"
        cursor.execute(sql, values)
        conn.commit()
        
        class Result:
            def __init__(self, count):
                self.deleted_count = count
        
        return Result(cursor.rowcount)

# Async wrapper functions (for compatibility with existing code)
async def get_users_collection():
    return SQLiteCollection("users")

async def get_companies_collection():
    return SQLiteCollection("companies")

async def get_claims_collection():
    return SQLiteCollection("claims")

async def get_claim_files_collection():
    return SQLiteCollection("claim_files")

async def get_status_history_collection():
    return SQLiteCollection("claim_status_history")

# Database class for compatibility
class Database:
    db = None
    
    @classmethod
    async def close_db(cls):
        close_db()