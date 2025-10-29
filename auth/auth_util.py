import pymysql
import bcrypt
from datetime import datetime
 
from utils.db_connection import get_connection
from utils.logger import log_activity, log_user_activity, log_db_operation, log_error
 
def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plaintext password with hashed password."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
 

@log_activity("auth")
def register_user(email: str, username: str, password: str, role: str = "passenger"):
    """Register a new user in the database."""
    conn = get_connection()
    if not conn:
        log_error("DatabaseError", "Could not connect to database during registration")
        return {"status": "error", "message": "Database connection failed"}
    
    cursor = conn.cursor()
 
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            log_user_activity("system", "registration_failed", f"Email already exists: {email}")
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
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        user_id = cursor.fetchone()["LAST_INSERT_ID()"]
        log_user_activity(user_id, "registration_successful", f"User registered with role: {role}")
        log_db_operation("INSERT", "users", "success", f"New user registered: {username}")
        
        return {"status": "success", "message": "User registered successfully"}
 
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
 
    finally:
        cursor.close()
        conn.close()
 

@log_activity("auth")
def login_user(email: str, password: str):
    """Authenticate user credentials and return status."""
    conn = get_connection()
    if not conn:
        log_error("DatabaseError", "Could not connect to database during login")
        return {"status": "error", "message": "Database connection failed"}
    
    cursor = conn.cursor()
 
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s AND isActive = 1", (email,))
        user = cursor.fetchone()
 
        if not user:
            log_user_activity("system", "login_failed", f"User not found or inactive: {email}")
            return {"status": "error", "message": "User not found or inactive"}
 
        if not verify_password(password, user["password"]):
            log_user_activity(user["user_id"], "login_failed", "Incorrect password")
            return {"status": "error", "message": "Incorrect password"}
 
        now = datetime.now()
        cursor.execute(
            "UPDATE users SET last_login = %s, updatedAt = %s WHERE user_id = %s",
            (now, now, user["user_id"])
        )
        conn.commit()
        log_db_operation("UPDATE", "users", "success", f"Updated last_login for user: {user['user_id']}")
 
        user.pop("password", None)
        log_user_activity(user["user_id"], "login_successful", f"Login at {now}")
        return {"status": "success", "user": user}
 
    except Exception as e:
        return {"status": "error", "message": str(e)}
 
    finally:
        cursor.close()
        conn.close()
 
@log_activity("auth")
def logout_user(user_id: int):
    """Logs out a user."""
    conn = get_connection()
    if not conn:
        log_error("DatabaseError", "Could not connect to database during logout")
        return {"status": "error", "message": "Database connection failed"}
    
    cursor = conn.cursor()

    try:
        now = datetime.now()
        cursor.execute(
            "UPDATE users SET last_logout = %s, updatedAt = %s WHERE user_id = %s",
            (now, now, user_id)
        )
        conn.commit()
        log_db_operation("UPDATE", "users", "success", f"Updated last_logout for user: {user_id}")
        log_user_activity(user_id, "logout_successful", f"Logout at {now}")
        return {"status": "success", "message": "Logged out successfully"}

    except Exception as e:
        conn.rollback()
        log_error("LogoutError", f"Failed to log out user {user_id}: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    reg = register_user("test@example.com", "john_doe", "secure123", "passenger")
    print(reg)
 
    login = login_user("test@example.com", "secure123")
    print(login)