from utils.db_connection import get_connection
 
def execute_query(query, params=None):
    conn, cursor = get_connection()
    if not conn:
        return False
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        print("Error executing query:", e)
        return False
    finally:
        conn.close()
 
def fetch_one(query, params=None):
    conn, cursor = get_connection()
    if not conn:
        return None
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    except Exception as e:
        print("Error fetching record:", e)
        return None
    finally:
        conn.close()
 
def fetch_all(query, params=None):
    conn, cursor = get_connection()
    if not conn:
        return []
    try:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    except Exception as e:
        print("Error fetching all records:", e)
        return []
    finally:
        conn.close()