import pymysql
import bcrypt
import datetime
from utils.db_connection import get_connection
 
def get_cursor():
    conn = get_connection()
    if not conn:
        return None, None
    return conn, conn.cursor()
 
def hash_password(password: str) -> str:
    """Hashes password securely using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
 
def check_password(password: str, hashed: str) -> bool:
    """Verifies password against stored bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return False
 
def load_users() -> dict:
    """Load all users into a dictionary"""
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return {}
 
    cursor.execute("SELECT user_id, name, email, password, role, is_active FROM users")
    users = {row["email"]: row for row in cursor.fetchall()}
 
    conn.close()
    return users
 
def save_user(name: str, email: str, password: str, role: str) -> bool:
    """Registers a new user and inserts into role-specific table."""
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return False
 
    hashed_pw = hash_password(password)
    now = datetime.datetime.now()
 
    try:
        cursor.execute("""
            INSERT INTO users (name, email, password, role, created_at, updated_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, hashed_pw, role, now, now, True))
 
        user_id = cursor.lastrowid
 
        if role == "driver":
            cursor.execute("INSERT INTO drivers (user_id, avg_rating, total_rides) VALUES (%s, 0, 0)", (user_id,))
        elif role == "passenger":
            cursor.execute("INSERT INTO passengers (user_id, avg_rating, total_rides) VALUES (%s, 0, 0)", (user_id,))
        elif role == "both":
            cursor.execute("INSERT INTO drivers (user_id, avg_rating, total_rides) VALUES (%s, 0, 0)", (user_id,))
            cursor.execute("INSERT INTO passengers (user_id, avg_rating, total_rides) VALUES (%s, 0, 0)", (user_id,))
 
        conn.commit()
        return True
 
    except pymysql.IntegrityError:
        conn.rollback()
        return False
 
    finally:
        conn.close()
 
def authenticate_user(email: str, password: str):
    """Checks user credentials and returns user data if valid."""
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return None
 
    cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = TRUE", (email,))
    user = cursor.fetchone()
    conn.close()
 
    if user and check_password(password, user["password"]):
        update_last_login(user["user_id"])
        return user
 
    return None
 
def update_last_login(user_id: int):
    """Updates last login timestamp for a user."""
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return
 
    now = datetime.datetime.now()
    cursor.execute("UPDATE users SET updated_at = %s WHERE user_id = %s", (now, user_id))
    conn.commit()
    conn.close()