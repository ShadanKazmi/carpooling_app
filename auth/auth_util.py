import pymysql
import bcrypt
from datetime import datetime
 
from utils.db_connection import get_connection
 
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plaintext password with hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
 

def register_user(email: str, username: str, password: str, role: str = "passenger"):
    """Register a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return {"status": "error", "message": "Email already registered"}
 
        hashed_pw = hash_password(password)
 
        now = datetime.now()
        cursor.execute(
            """
            INSERT INTO users (email, username, password, role, createdAt, updatedAt, last_login, isActive)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (email, username, hashed_pw, role, now, now, None, 1)
        )
        conn.commit()
        return {"status": "success", "message": "User registered successfully"}
 
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
 
    finally:
        cursor.close()
        conn.close()
 

def login_user(email: str, password: str):
    """Authenticate user credentials and return status."""
    conn = get_connection()
    cursor = conn.cursor()
 
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND isActive = 1", (email,))
        user = cursor.fetchone()
 
        if not user:
            return {"status": "error", "message": "User not found or inactive"}
 
        if not verify_password(password, user["password"]):
            return {"status": "error", "message": "Incorrect password"}
 
        cursor.execute(
            "UPDATE users SET last_login = %s, updatedAt = %s WHERE user_id = %s",
            (datetime.now(), datetime.now(), user["user_id"])
        )
        conn.commit()
 
        user.pop("password", None)
        return {"status": "success", "user": user}
 
    except Exception as e:
        return {"status": "error", "message": str(e)}
 
    finally:
        cursor.close()
        conn.close()
 
if __name__ == "__main__":
    reg = register_user("test@example.com", "john_doe", "secure123", "passenger")
    print(reg)
 
    login = login_user("test@example.com", "secure123")
    print(login)