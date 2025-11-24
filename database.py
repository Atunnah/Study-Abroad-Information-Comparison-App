import sqlite3
from tkinter import messagebox
import hashlib

DB_FILE = "universities_db.db"
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # --------------------------
    # 1. User table
    # --------------------------
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

    # --------------------------
    # 2. Countries table
    # --------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        flag_url TEXT
    )
    """)

    # --------------------------
    # 3. Universities table
    # --------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS universities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country_id INTEGER,
        state TEXT,
        domain TEXT,
        website TEXT,
        num_majors INTEGER,
        tuition_fee_avg REAL,
        entry_requirements TEXT,
        FOREIGN KEY(country_id) REFERENCES countries(id)
    )
    """)

    # --------------------------
    # 4. Scholarships table
    # --------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        university_id INTEGER,
        value REAL,
        duration TEXT,
        criteria TEXT,
        FOREIGN KEY(university_id) REFERENCES universities(id)
    )
    """)

    # --------------------------
    # 5. Create default admin account
    # --------------------------
    cur.execute("SELECT * FROM user WHERE email = ?", ("admin",))
    if not cur.fetchone():
        admin_pass = hash_password("ad123")
        cur.execute("""
            INSERT INTO user (email, password, full_name, is_admin) 
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_pass, "Administrator", 1))
        print("✅ Created admin accout")
        
        
     # --------------------------
     # 6. User Favorite Universities (Many-to-Many)
     # --------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            university_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, university_id),
            FOREIGN KEY(user_id) REFERENCES user(uid),
            FOREIGN KEY(university_id) REFERENCES universities(id)
            )
      """)


    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


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
    
    
def add_favorite(uid, university_id):
    return execute_db("""
        INSERT OR IGNORE INTO user_favorites (user_id, university_id)
        VALUES (?, ?)
    """, (uid, university_id))


def remove_favorite(uid, university_id):
    return execute_db("""
        DELETE FROM user_favorites
        WHERE user_id = ? AND university_id = ?
    """, (uid, university_id))

def get_user_favorites(uid):
    return execute_db("""
        SELECT 
            universities.id, 
            universities.name, 
            countries.name,
            user_favorites.created_at
        FROM user_favorites
        JOIN universities 
            ON user_favorites.university_id = universities.id
        LEFT JOIN countries 
            ON universities.country_id = countries.id
        WHERE user_favorites.user_id = ?
        ORDER BY user_favorites.created_at DESC
    """, (uid,), fetch=True)

