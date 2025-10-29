import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv
 
load_dotenv()
 
def get_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            cursorclass=DictCursor,
            autocommit=True
        )
        print("Database connection established successfully.")
        return connection
    except pymysql.MySQLError as e:
        print("Error connecting to MySQL:", e)
        return None