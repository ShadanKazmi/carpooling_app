from utils.db_connection import get_connection, close_connection

def test_database_connection():
    conn = get_connection()
    
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"Found {len(users)} users")
        print(users)
        cursor.close()
        close_connection(conn)

if __name__ == "__main__":
    test_database_connection()