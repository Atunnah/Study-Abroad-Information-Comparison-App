import sqlite3
from tkinter import messagebox
import hashlib

DB_FILE = "universities.db"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize all database tables"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # User table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        address TEXT,
        phone TEXT,
        is_admin BOOLEAN DEFAULT 0
    )
    """)
    
    # Countries table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        flag_url TEXT
    )
    """)
    
    # Universities table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS universities_basic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        country_id INTEGER,
        state TEXT,
        domain TEXT,
        website TEXT,
        FOREIGN KEY(country_id) REFERENCES countries(id)
    )
    """)
    
    # Create default admin account if not exists
    cur.execute("SELECT * FROM user WHERE email = ?", ("admin",))
    if not cur.fetchone():
        admin_pass = hash_password("ad123")
        cur.execute("""
            INSERT INTO user (email, password, full_name, is_admin) 
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_pass, "Administrator", 1))
    
    conn.commit()
    conn.close()

def execute_db(query, params=(), fetch=False):
    """Execute database query"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            conn.close()
            return result
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        messagebox.showerror("DB Error", str(e))
        return None

def register_user(email, password, full_name, address, phone):
    """Register new user"""
    hashed_pass = hash_password(password)
    return execute_db("""
        INSERT INTO user (email, password, full_name, address, phone) 
        VALUES (?, ?, ?, ?, ?)
    """, (email, hashed_pass, full_name, address, phone))

def login_user(email, password):
    """Login user and return user data"""
    hashed_pass = hash_password(password)
    result = execute_db("""
        SELECT uid, email, full_name, address, phone, is_admin 
        FROM user WHERE email = ? AND password = ?
    """, (email, hashed_pass), fetch=True)
    return result[0] if result else None

def get_all_users():
    """Get all non-admin users"""
    return execute_db("""
        SELECT uid, email, full_name, address, phone 
        FROM user WHERE is_admin = 0
    """, fetch=True)

def delete_user(uid):
    """Delete user by uid"""
    return execute_db("DELETE FROM user WHERE uid = ?", (uid,))

def update_user_profile(uid, full_name, address, phone):
    """Update user profile"""
    return execute_db("""
        UPDATE user SET full_name = ?, address = ?, phone = ? 
        WHERE uid = ?
    """, (full_name, address, phone, uid))