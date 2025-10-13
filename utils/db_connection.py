import pymysql
from pymysql import Error

def get_connection():
    """
    Establishes and returns a connection to the carpool_db database.
    
    Returns:
        connection: MySQL database connection object
    """
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='carpool_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        if connection:
            print("Database connection successful!")
            return connection
            
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def close_connection(connection):
    """
    Closes the database connection.
    
    Args:
        connection: MySQL database connection object
    """
    if connection:
        connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    conn = get_connection()
    
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"Connected to database: {db_name}")
        cursor.close()
        close_connection(conn)