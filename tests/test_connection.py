from utils.db_connection import get_connection
 
def test_connection():
    conn, cursor = get_connection()
    if conn is None:
        print("❌ Connection failed.")
        return
 
    try:
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"✅ Connected to database: {db_name['DATABASE()']}")
 
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("\n📋 Tables in your database:")
        for t in tables:
            print("-", list(t.values())[0])
 
    except Exception as e:
        print("⚠️ Error running test query:", e)
    finally:
        conn.close()
        print("🔒 Connection closed.")
 
if __name__ == "__main__":
    test_connection()