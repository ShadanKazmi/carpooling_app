import datetime
import json
import pymysql
from utils.db_connection import get_connection

def get_driver_id(user_id):
    """Fetch the driver's ID using the linked user_id."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT driver_id FROM drivers WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result["driver_id"] if result else None
    except Exception as e:
        print("Error fetching driver_id:", e)
        return None
    finally:
        cursor.close()
        conn.close()

def fetch_routes():
    """Fetch all available routes."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = "SELECT route_id, from_city, to_city, distance_km, duration_min FROM routes ORDER BY created_at DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching routes:", e)
        return []
    finally:
        cursor.close()
        conn.close()

def create_ride_request(passenger_id, from_city, to_city, date_time, passengers_count, preferences):
    """Create a new ride request from a passenger."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            INSERT INTO ride_requests
            (passenger_id, from_city, to_city, date_time, passengers_count, preferences, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            passenger_id,
            from_city,
            to_city,
            date_time,
            passengers_count,
            json.dumps(preferences),
            "pending",
            datetime.datetime.now()
        ))
        conn.commit()
        return True
    except Exception as e:
        print("Error creating ride request:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
 

def create_ride_offer(driver_id, vehicle_no, route_id, available_seats, price_per_km, estimated_fare):
    """Create a new ride offer by a driver."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            INSERT INTO ride_offers
            (driver_id, vehicle_no, route_id, available_seats, price_per_km, estimated_fare, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            driver_id,
            vehicle_no,
            route_id,
            available_seats,
            price_per_km,
            estimated_fare,
            "open",
            datetime.datetime.now()
        ))
        conn.commit()
        return True
    except Exception as e:
        print("Error creating ride offer:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
 

def get_open_ride_requests():
    """Fetch all ride requests that are not yet matched."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT * FROM ride_requests WHERE status = 'pending' ORDER BY created_at DESC"
        )
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching open ride requests:", e)
        return []
    finally:
        cursor.close()
        conn.close()
 

def get_open_ride_offers():
    """Fetch all open ride offers with route information."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            SELECT ro.offer_id, ro.driver_id, ro.vehicle_no, ro.available_seats,
                   ro.price_per_km, ro.estimated_fare, ro.status, r.from_city, r.to_city
            FROM ride_offers ro
            JOIN routes r ON ro.route_id = r.route_id
            WHERE ro.status = 'open'
            ORDER BY ro.created_at DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching open ride offers:", e)
        return []
    finally:
        cursor.close()
        conn.close()