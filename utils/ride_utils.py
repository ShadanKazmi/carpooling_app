import datetime
import json
import pymysql
import streamlit as st
from utils.db_connection import get_connection
 
 
def get_driver_id(user_id):
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

def fetch_route_cities():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT DISTINCT from_city FROM routes ORDER BY from_city ASC;")
        from_cities = [row["from_city"] for row in cursor.fetchall()]
 
        cursor.execute("SELECT DISTINCT to_city FROM routes ORDER BY to_city ASC;")
        to_cities = [row["to_city"] for row in cursor.fetchall()]
 
        return from_cities, to_cities
    except Exception as e:
        st.error(f"Error fetching routes: {e}")
        return [], []
    finally:
        cursor.close()
        conn.close()
 
 
def create_ride_request(passenger_id, from_city, to_city, date_time, passengers_count, preferences):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            INSERT INTO ride_requests (passenger_id, from_city, to_city, date_time, passengers_count, preferences, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
        """
        cursor.execute(query, (
            passenger_id, from_city, to_city, date_time,
            passengers_count, json.dumps(preferences),
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
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            INSERT INTO ride_offers (driver_id, vehicle_no, route_id, available_seats, price_per_km, estimated_fare, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'open', NOW())
        """
        cursor.execute(query, (
            driver_id, vehicle_no, route_id, available_seats, price_per_km, estimated_fare
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
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM ride_requests WHERE status = 'pending' ORDER BY created_at DESC")
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching open ride requests:", e)
        return []
    finally:
        cursor.close()
        conn.close()
 
 
def get_open_ride_offers():
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            SELECT ro.offer_id, ro.driver_id, ro.vehicle_no, ro.available_seats, ro.price_per_km, ro.estimated_fare, ro.status,
                   r.from_city, r.to_city
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
 
 
def get_matched_ride_details(request_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
            SELECT rr.request_id, rr.from_city, rr.to_city, rr.date_time,
                   ro.offer_id, ro.vehicle_no, ro.price_per_km, ro.estimated_fare,
                   ro.available_seats, u.name AS driver_name, d.avg_rating, d.total_rides
            FROM ride_requests rr
            JOIN ride_offers ro ON rr.request_id = ro.request_id
            JOIN drivers d ON ro.driver_id = d.driver_id
            JOIN users u ON d.user_id = u.user_id
            WHERE rr.request_id = %s
        """
        cursor.execute(query, (request_id,))
        return cursor.fetchone()
    except Exception as e:
        print("❌ Error fetching matched ride details:", e)
        return None
    finally:
        cursor.close()
        conn.close()
 
 
def accept_ride_request(driver_id, request_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM ride_requests WHERE request_id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            st.error("Ride request not found.")
            return False
 
        cursor.execute("SELECT route_id, distance_km FROM routes WHERE from_city = %s AND to_city = %s",
                       (req["from_city"], req["to_city"]))
        route = cursor.fetchone()
        if not route:
            st.error("No matching route found for this request.")
            return False
 
        distance_km = route["distance_km"]
        price_per_km = 10.0
        estimated_fare = round(distance_km * price_per_km, 2)
 
        cursor.execute("""
            INSERT INTO ride_offers (driver_id, vehicle_no, route_id, request_id, available_seats, price_per_km, estimated_fare, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'booked', NOW())
        """, (driver_id, f"DRV{driver_id}-REQ{request_id}", route["route_id"], request_id,
              req["passengers_count"], price_per_km, estimated_fare))
        offer_id = cursor.lastrowid
 
        cursor.execute("""
            INSERT INTO rides (offer_id, passenger_id, driver_id, seats_booked, total_fare, start_time, status)
            VALUES (%s, %s, %s, %s, %s, NOW(), 'active')
        """, (offer_id, req["passenger_id"], driver_id, req["passengers_count"], estimated_fare))
 
        cursor.execute("UPDATE ride_requests SET status = 'matched' WHERE request_id = %s", (request_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error accepting ride request: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_driver_assigned_rides(driver_id):
    """Fetch all active or booked rides assigned to the driver."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
        SELECT r.ride_id, r.offer_id, r.passenger_id, r.status, r.start_time, r.end_time,
               rr.from_city, rr.to_city, u.name AS passenger_name
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN users u ON rr.passenger_id = u.user_id
        WHERE r.driver_id = %s AND r.status IN ('active', 'booked')
        ORDER BY r.start_time DESC
        """
        cursor.execute(query, (driver_id,))
        return cursor.fetchall()
    except Exception as e:
        print("Error fetching assigned rides:", e)
        return []
    finally:
        cursor.close()
        conn.close()
 
 
def update_ride_status(ride_id, new_status):
    """Update ride and offer status simultaneously."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if new_status == "active":
            cursor.execute("""
                UPDATE rides r
                JOIN ride_offers ro ON r.offer_id = ro.offer_id
                SET r.status = 'active', ro.status = 'active', r.start_time = NOW()
                WHERE r.ride_id = %s
            """, (ride_id,))
        elif new_status == "completed":
            cursor.execute("""
                UPDATE rides r
                JOIN ride_offers ro ON r.offer_id = ro.offer_id
                SET r.status = 'completed', ro.status = 'completed', r.end_time = NOW()
                WHERE r.ride_id = %s
            """, (ride_id,))
        elif new_status == "cancelled":
            cursor.execute("""
                UPDATE rides r
                JOIN ride_offers ro ON r.offer_id = ro.offer_id
                SET r.status = 'cancelled', ro.status = 'cancelled'
                WHERE r.ride_id = %s
            """, (ride_id,))
        else:
            raise ValueError("Invalid ride status")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error updating ride status:", e)
        return False
    finally:
        cursor.close()
        conn.close()