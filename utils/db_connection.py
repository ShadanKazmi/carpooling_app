"""
Database Connection Module for Carpooling Application
Path: utils/db_connection.py
Handles MySQL database connections and operations
"""

import pymysql
from pymysql import Error
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'carpool'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# ============================================
# GET DATABASE CONNECTION
# ============================================
def get_connection():
    """
    Establishes and returns a connection to the carpool database.
    
    Returns:
        pymysql.connections.Connection: MySQL database connection object
        None: If connection fails
        
    Raises:
        pymysql.Error: If connection error occurs
    """
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=DB_CONFIG['cursorclass']
        )
        
        if connection:
            logger.info("✅ Database connection successful!")
            return connection
            
    except Error as e:
        logger.error(f"❌ Error connecting to database: {e}")
        return None

# ============================================
# GET DATABASE CURSOR
# ============================================
def get_cursor(connection):
    """
    Get a cursor object from the database connection.
    
    Args:
        connection (pymysql.connections.Connection): Database connection object
        
    Returns:
        pymysql.cursors.DictCursor: Cursor object for executing queries
        None: If connection is invalid
    """
    try:
        if connection:
            cursor = connection.cursor()
            logger.info("✅ Cursor created successfully!")
            return cursor
        else:
            logger.error("❌ Connection object is None")
            return None
    except Error as e:
        logger.error(f"❌ Error creating cursor: {e}")
        return None

# ============================================
# CLOSE DATABASE CONNECTION
# ============================================
def close_connection(connection):
    """
    Closes the database connection gracefully.
    
    Args:
        connection (pymysql.connections.Connection): MySQL database connection object
        
    Returns:
        bool: True if closed successfully, False otherwise
    """
    if connection:
        try:
            connection.close()
            logger.info("✅ Database connection closed.")
            return True
        except Error as e:
            logger.error(f"❌ Error closing connection: {e}")
            return False
    else:
        logger.warning("⚠️ Connection object is None, nothing to close.")
        return False

# ============================================
# EXECUTE QUERY (SELECT)
# ============================================
def execute_query(query, params=None):
    """
    Execute a SELECT query and return results.
    
    Args:
        query (str): SQL SELECT query
        params (tuple): Query parameters for parameterized queries (optional)
        
    Returns:
        list: List of dictionaries containing query results
        None: If query execution fails
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = get_cursor(connection)
        if not cursor:
            return None
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        logger.info(f"✅ Query executed successfully. Rows returned: {len(results)}")
        
        cursor.close()
        close_connection(connection)
        
        return results
        
    except Error as e:
        logger.error(f"❌ Error executing query: {e}")
        return None

# ============================================
# EXECUTE UPDATE/INSERT/DELETE
# ============================================
def execute_update(query, params=None):
    """
    Execute INSERT, UPDATE, or DELETE query.
    
    Args:
        query (str): SQL INSERT/UPDATE/DELETE query
        params (tuple): Query parameters for parameterized queries (optional)
        
    Returns:
        int: Number of affected rows
        None: If query execution fails
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = get_cursor(connection)
        if not cursor:
            return None
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        connection.commit()
        affected_rows = cursor.rowcount
        
        logger.info(f"✅ Update executed successfully. Rows affected: {affected_rows}")
        
        cursor.close()
        close_connection(connection)
        
        return affected_rows
        
    except Error as e:
        logger.error(f"❌ Error executing update: {e}")
        if connection:
            connection.rollback()
            close_connection(connection)
        return None

# ============================================
# EXECUTE INSERT & GET LAST ID
# ============================================
def execute_insert(query, params=None):
    """
    Execute INSERT query and return the last inserted ID.
    
    Args:
        query (str): SQL INSERT query
        params (tuple): Query parameters for parameterized queries (optional)
        
    Returns:
        int: Last inserted ID (primary key)
        None: If insertion fails
    """
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = get_cursor(connection)
        if not cursor:
            return None
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        connection.commit()
        last_id = cursor.lastrowid
        
        logger.info(f"✅ Insert executed successfully. Last ID: {last_id}")
        
        cursor.close()
        close_connection(connection)
        
        return last_id
        
    except Error as e:
        logger.error(f"❌ Error executing insert: {e}")
        if connection:
            connection.rollback()
            close_connection(connection)
        return None

# ============================================
# TEST CONNECTION
# ============================================
def test_connection():
    """
    Test database connection and verify carpool database exists.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        connection = get_connection()
        
        if not connection:
            logger.error("❌ Database connection test: FAILED - Could not establish connection")
            return False
        
        cursor = get_cursor(connection)
        
        if not cursor:
            logger.error("❌ Database connection test: FAILED - Could not create cursor")
            return False
        
        # Test query
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        
        if db_name:
            logger.info(f"✅ Database connection test: SUCCESS")
            logger.info(f"✅ Connected to database: {db_name.get('DATABASE()', 'Unknown')}")
        
        cursor.close()
        close_connection(connection)
        
        return True
        
    except Error as e:
        logger.error(f"❌ Database connection test: FAILED - {e}")
        return False

# ============================================
# VERIFY TABLES
# ============================================
def verify_tables():
    """
    Verify that all required tables exist in the database.
    
    Returns:
        dict: Dictionary with table names and existence status
    """
    required_tables = [
        'passengers',
        'drivers',
        'vehicles',
        'routes',
        'ride_requests',
        'ride_offers',
        'rides',
        'ratings'
    ]
    
    connection = get_connection()
    if not connection:
        logger.error("❌ Could not establish connection to verify tables")
        return {}
    
    try:
        cursor = get_cursor(connection)
        if not cursor:
            return {}
        
        tables_status = {}
        
        for table in required_tables:
            query = f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            
            cursor.execute(query, (DB_CONFIG['database'], table))
            result = cursor.fetchone()
            
            tables_status[table] = bool(result)
            status_icon = "✅" if tables_status[table] else "❌"
            logger.info(f"{status_icon} Table '{table}' exists: {bool(result)}")
        
        cursor.close()
        close_connection(connection)
        
        return tables_status
        
    except Error as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return {}

# ============================================
# GET DATABASE STATISTICS
# ============================================
def get_database_stats():
    """
    Get statistics about the database (row counts for each table).
    
    Returns:
        dict: Dictionary with table names and row counts
    """
    tables = [
        'passengers',
        'drivers',
        'vehicles',
        'routes',
        'ride_requests',
        'ride_offers',
        'rides',
        'ratings'
    ]
    
    stats = {}
    
    for table in tables:
        try:
            result = execute_query(f"SELECT COUNT(*) as count FROM {table}")
            if result:
                stats[table] = result[0]['count']
            else:
                stats[table] = 0
        except Exception as e:
            logger.error(f"Error getting stats for {table}: {e}")
            stats[table] = 0
    
    return stats

# ============================================
# .ENV FILE TEMPLATE
# ============================================
"""
ENVIRONMENT VARIABLES TEMPLATE (.env)

# MySQL Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=carpool

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_LOGGER_LEVEL=info

# Application Settings
DEBUG=True
"""

# ============================================
# MAIN - TEST CONNECTION
# ============================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("CARPOOL DATABASE CONNECTION TEST")
    print("="*50 + "\n")
    
    # Test connection
    print("[1] Testing database connection...")
    if test_connection():
        print("✅ Connection test passed!\n")
    else:
        print("❌ Connection test failed!\n")
    
    # Verify tables
    print("[2] Verifying database tables...")
    tables_status = verify_tables()
    
    if all(tables_status.values()):
        print("✅ All tables exist!\n")
    else:
        print("❌ Some tables are missing!\n")
    
    # Get statistics
    print("[3] Database statistics...")
    stats = get_database_stats()
    for table, count in stats.items():
        print(f"   {table}: {count} rows")
    
    print("\n" + "="*50)
    print("✅ DATABASE CHECK COMPLETE")
    print("="*50 + "\n")