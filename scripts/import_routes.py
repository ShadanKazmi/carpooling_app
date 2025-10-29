import os
import sys
import json
import datetime
import pymysql

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
 
from utils.db_connection import get_connection
 
with open("model/static_routes_dataset.json", "r", encoding="utf-8") as file:
    routes_data = json.load(file)
 
conn = get_connection()
if not conn:
    print("Could not connect to the database.")
    exit()
 
cursor = conn.cursor()
 
insert_query = """
    INSERT INTO routes (from_city, to_city, distance_km, duration_min, coordinates, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
 
count = 0
for route in routes_data:
    try:
        from_city = route.get("from_city")
        to_city = route.get("to_city")
        distance_km = route.get("distance_km")
        duration_min = route.get("duration_min")
        coordinates = json.dumps(route.get("coordinates_lonlat"))  # store as JSON string
        created_at = datetime.datetime.now()
 
        cursor.execute(insert_query, (from_city, to_city, distance_km, duration_min, coordinates, created_at))
        count += 1
 
    except Exception as e:
        print(f"Error inserting route {from_city} → {to_city}: {e}")
 
conn.commit()
conn.close()

print(f"Successfully inserted {count} routes into the database.")