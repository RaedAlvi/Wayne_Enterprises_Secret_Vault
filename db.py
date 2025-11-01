import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import os

DB_PATH = "wayne_vault.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def add_missing_columns():
    """Add missing columns to the users and transactions tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if the column exists and add it if necessary for users table
    try:
        cursor.execute("PRAGMA table_info(users);")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add failed_login_attempts and lockout_until columns if missing
        if "failed_login_attempts" not in columns:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
            """)
        
        if "lockout_until" not in columns:
            cursor.execute("""
                ALTER TABLE users ADD COLUMN lockout_until TIMESTAMP;
            """)

        # Check if user_email column exists in transactions table
        cursor.execute("PRAGMA table_info(transactions);")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_email" not in columns:
            cursor.execute("""
                ALTER TABLE transactions ADD COLUMN user_email TEXT NOT NULL;
            """)
        
        conn.commit()
    except Exception as e:
        print(f"Error adding missing columns: {e}")
    
    conn.close()

def init_db():
    """Initialize database with all required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create the users table with the required columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_secret TEXT NOT NULL,
            failed_login_attempts INTEGER DEFAULT 0,
            lockout_until TIMESTAMP,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create the transactions table with the correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            amount REAL CHECK(amount > 0) NOT NULL,
            category TEXT CHECK(LENGTH(category) <= 50) NOT NULL,
            note_encrypted TEXT CHECK(LENGTH(note_encrypted) <= 1000),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)
    
    # Create the audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            action TEXT NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

    # Add missing columns to the users and transactions tables (if any)
    add_missing_columns()

# User Management
def user_exists(email: str) -> bool:
    """Check if user exists"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_user(email: str, password_hash: str, totp_secret: str, role: str = 'user') -> bool:
    """Create new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, password_hash, totp_secret, role) 
            VALUES (?, ?, ?, ?)
        """, (email, password_hash, totp_secret, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def get_user(email: str) -> Optional[Tuple]:
    """Get user by email"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, password_hash, totp_secret, 
               failed_login_attempts, lockout_until, role
        FROM users WHERE email = ?
    """, (email,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_failed_attempts(email: str, attempts: int):
    """Update failed login attempts"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if attempts >= 5:
        # Lock account for 15 minutes
        lockout_until = datetime.now() + timedelta(minutes=15)
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = ?, lockout_until = ?
            WHERE email = ?
        """, (attempts, lockout_until, email))
    else:
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = ?
            WHERE email = ?
        """, (attempts, email))
    
    conn.commit()
    conn.close()

def reset_failed_attempts(email: str):
    """Reset failed login attempts"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET failed_login_attempts = 0, lockout_until = NULL
        WHERE email = ?
    """, (email,))
    conn.commit()
    conn.close()

def is_account_locked(email: str) -> bool:
    """Check if account is locked"""
    user = get_user(email)
    if not user:
        return False
    
    lockout_until = user[5]
    if lockout_until:
        lockout_time = datetime.strptime(lockout_until, '%Y-%m-%d %H:%M:%S.%f')
        if datetime.now() < lockout_time:
            return True
        else:
            # Unlock account
            reset_failed_attempts(email)
    
    return False

# Transaction Management
def add_transaction(user_email: str, txn_type: str, amount: float, 
                   category: str, note_encrypted: Optional[str] = None) -> bool:
    """Add new transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_email, type, amount, category, note_encrypted)
            VALUES (?, ?, ?, ?, ?)
        """, (user_email, txn_type, amount, category, note_encrypted))
        conn.commit()
        conn.close()
        
        log_audit(user_email, f"Transaction added: {txn_type} ${amount}", "0.0.0.0")
        return True
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return False

def get_transactions(user_email: str) -> List[Tuple]:
    """List all transactions for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_email, type, amount, category, note_encrypted, created_at
        FROM transactions
        WHERE user_email = ?
        ORDER BY created_at DESC
    """, (user_email,))
    results = cursor.fetchall()
    conn.close()
    return results

# Audit Logging
def log_audit(user_email: str, action: str, ip_address: str):
    """Log audit event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_email, action, ip_address)
            VALUES (?, ?, ?)
        """, (user_email, action, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging audit: {e}")

def get_audit_logs(user_email: Optional[str] = None, admin: bool = False) -> List[Tuple]:
    """Get audit logs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if admin:
        cursor.execute("""
            SELECT id, user_email, action, ip_address, created_at
            FROM audit_logs
            ORDER BY created_at DESC
            LIMIT 100
        """)
    else:
        cursor.execute("""
            SELECT id, user_email, action, ip_address, created_at
            FROM audit_logs
            WHERE user_email = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_email,))

    results = cursor.fetchall()
    conn.close()
    return results
