import re
import bcrypt
import datetime
import pymysql
from utils.db_connection import get_connection
 
def get_cursor():
    conn = get_connection()
    if not conn:
        return None, None
    return conn, conn.cursor(pymysql.cursors.DictCursor)
 
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
 
def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return False
 
def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
 
def is_valid_password(password: str) -> bool:
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
    return re.match(pattern, password) is not None
 
def load_users() -> dict:
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return {}
    cursor.execute("SELECT user_id, name, email, password, role, is_active FROM users")
    users = {row["email"]: row for row in cursor.fetchall()}
    conn.close()
    return users
 
def save_user(name: str, email: str, password: str, role: str) -> bool:
    if not is_valid_email(email):
        raise ValueError("Invalid email address")
 
    if not is_valid_password(password):
        raise ValueError("Password must be at least 8 characters long, "
                         "contain 1 uppercase, 1 lowercase, and 1 number")
 
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
    conn, cursor = get_cursor()
    if not conn or not cursor:
        return
    now = datetime.datetime.now()
    cursor.execute("UPDATE users SET updated_at = %s WHERE user_id = %s", (now, user_id))
    conn.commit()
    conn.close()