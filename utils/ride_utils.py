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

 
def get_route_coordinates(route_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    cursor.execute("SELECT coordinates FROM routes WHERE route_id=%s", (route_id,))
    row = cursor.fetchone()
 
    cursor.close()
    conn.close()
 
    if not row or not row["coordinates"]:
        return []
 
    coords = row["coordinates"]
 
    if isinstance(coords, str):
        coords = json.loads(coords)
 
    formatted = []
    for pair in coords:
        if isinstance(pair, list) and len(pair) == 2:
            lon, lat = pair
            formatted.append({"lat": float(lat), "lon": float(lon)})
 
    return formatted
 
def create_ride_request(passenger_id, from_city, to_city, date_time, passengers_count, preferences):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    try:
        cursor.execute("SELECT passenger_id FROM passengers WHERE user_id = %s", (passenger_id,))
        passenger = cursor.fetchone()
 
        if not passenger:
            print("No matching passenger found for user_id:", passenger_id)
            return False
 
        actual_passenger_id = passenger["passenger_id"]
 
        query = """
            INSERT INTO ride_requests
            (passenger_id, from_city, to_city, date_time, passengers_count, preferences, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
        """
        cursor.execute(query, (
            actual_passenger_id,
            from_city,
            to_city,
            date_time,
            passengers_count,
            json.dumps(preferences),
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
        print("Error fetching matched ride details:", e)
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

def get_available_rides(from_city, to_city, date_time, passengers_count):
    """
    Fetch ride offers matching route and date with enough available seats.
    """
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
        SELECT r.*, d.name AS driver_name, d.avg_rating, d.total_rides
        FROM ride_offers r
        JOIN drivers d ON r.driver_id = d.user_id
        JOIN routes rt ON r.route_id = rt.route_id
        WHERE rt.from_city = %s AND rt.to_city = %s
        AND r.status IN ('open', 'booked')
        AND r.available_seats >= %s
        AND DATE(r.accepted_at) = %s
        ORDER BY r.accepted_at ASC
    """
    cursor.execute(query, (from_city, to_city, passengers_count, date_time.date()))
    rides = cursor.fetchall()
    cursor.close()
    conn.close()
    return rides


def find_matching_offers(from_city, to_city, date_time, passengers_count):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = """
        SELECT ro.offer_id, ro.driver_id, ro.vehicle_no, ro.available_seats, ro.price_per_km, ro.estimated_fare,
               r.from_city, r.to_city, u.name AS driver_name
        FROM ride_offers ro
        JOIN routes r ON ro.route_id = r.route_id
        JOIN users u ON ro.driver_id = u.user_id
        WHERE r.from_city = %s AND r.to_city = %s
          AND ro.status IN ('open', 'booked')
          AND ro.available_seats >= %s
          AND DATE(ro.created_at) = DATE(%s)
        ORDER BY ro.estimated_fare ASC
        """
        cursor.execute(query, (from_city, to_city, passengers_count, date_time))
        return cursor.fetchall()
    except Exception as e:
        print("Error finding matching offers:", e)
        return []
    finally:
        cursor.close()
        conn.close()
 
 
def book_ride(offer_id, passenger_id, seats_requested):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT available_seats, estimated_fare, driver_id FROM ride_offers WHERE offer_id=%s", (offer_id,))
        offer = cursor.fetchone()
        if not offer or offer["available_seats"] < seats_requested:
            return False
 
        new_seats = offer["available_seats"] - seats_requested
        new_status = "booked" if new_seats > 0 else "full"
 
        cursor.execute("UPDATE ride_offers SET available_seats=%s, status=%s WHERE offer_id=%s",
                       (new_seats, new_status, offer_id))
 
        total_fare = offer["estimated_fare"]
        cursor.execute("""
            INSERT INTO rides (offer_id, passenger_id, driver_id, seats_booked, total_fare, start_time, status)
            VALUES (%s, %s, %s, %s, %s, NOW(), 'booked')
        """, (offer_id, passenger_id, offer["driver_id"], seats_requested, total_fare))
 
        cursor.execute("""
            UPDATE ride_requests SET status='matched'
            WHERE passenger_id=%s AND status='pending'
        """, (passenger_id,))
 
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error booking ride:", e)
        return False
    finally:
        cursor.close()
        conn.close()

def get_passenger_id_by_user(user_id: int):
    """Map users.user_id -> passengers.passenger_id"""
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("SELECT passenger_id FROM passengers WHERE user_id=%s", (user_id,))
        row = cur.fetchone()
        return row["passenger_id"] if row else None
    finally:
        cur.close()
        conn.close()
 
 
def has_user_already_rated(ride_id: int, rated_by_user_id: int) -> bool:
    """Check ratings table to avoid duplicate rating by same user for the same ride."""
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(
            "SELECT rating_id FROM ratings WHERE ride_id=%s AND rated_by=%s LIMIT 1",
            (ride_id, rated_by_user_id),
        )
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()
 
 
def save_rating_and_update_averages(
    ride_id: int,
    rated_by_user_id: int,
    rated_user_id: int,
    rating_value: int,
    feedback_text: str | None
) -> bool:
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(
            """
            INSERT INTO ratings (ride_id, rated_by, rated_user, rating, feedback, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (ride_id, rated_by_user_id, rated_user_id, rating_value, feedback_text),
        )
 
        cur.execute(
            "SELECT AVG(rating) AS avg_rating, COUNT(*) AS total FROM ratings WHERE rated_user=%s",
            (rated_user_id,)
        )
        agg = cur.fetchone() or {"avg_rating": None, "total": 0}
        new_avg = float(agg["avg_rating"]) if agg["avg_rating"] is not None else 0.0
        total_count = int(agg["total"])
 
        cur.execute("SELECT driver_id FROM drivers WHERE user_id=%s", (rated_user_id,))
        driver_row = cur.fetchone()
 
        if driver_row:
            cur.execute(
                "UPDATE drivers SET avg_rating=%s, total_rides=%s WHERE user_id=%s",
                (new_avg, total_count, rated_user_id),
            )
        else:
            cur.execute(
                "UPDATE passengers SET avg_rating=%s, total_rides=%s WHERE user_id=%s",
                (new_avg, total_count, rated_user_id),
            )
 
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("❌ save_rating error:", e)
        return False
    finally:
        cur.close()
        conn.close()
 
 
def get_rides_for_driver(driver_id: int):
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(
            """
            SELECT
                r.ride_id,
                r.status,
                r.seats_booked,
                r.total_fare,
                r.start_time,
                r.end_time,
                rr.from_city,
                rr.to_city,
                rr.date_time AS ride_date,
 
                -- passenger side
                u_p.name AS passenger_name,
                u_p.user_id AS passenger_user_id,
 
                -- driver side
                u_d.user_id AS driver_user_id
 
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
 
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN users   u_d ON d.user_id = u_d.user_id
 
            JOIN passengers p ON rr.passenger_id = p.passenger_id
            JOIN users      u_p ON p.user_id = u_p.user_id
 
            WHERE r.driver_id = %s
            ORDER BY COALESCE(r.start_time, rr.date_time) DESC, r.ride_id DESC
            """,
            (driver_id,),
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
 
 
def get_rides_for_passenger(passenger_id: int):
    conn = get_connection()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute(
            """
            SELECT
                r.ride_id,
                r.status,
                r.seats_booked,
                r.total_fare,
                r.start_time,
                r.end_time,
                rr.from_city,
                rr.to_city,
                rr.date_time AS ride_date,
 
                -- driver side
                u_d.name   AS driver_name,
                u_d.user_id AS driver_user_id,
 
                -- passenger side
                u_p.user_id AS passenger_user_id
 
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
 
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN users   u_d ON d.user_id = u_d.user_id
 
            JOIN passengers p ON r.passenger_id = p.passenger_id
            JOIN users      u_p ON p.user_id = u_p.user_id
 
            WHERE r.passenger_id = %s
            ORDER BY COALESCE(r.start_time, rr.date_time) DESC, r.ride_id DESC
            """,
            (passenger_id,),
        )
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def update_ride_position(ride_id, new_index):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE rides SET current_position_index=%s WHERE ride_id=%s", (new_index, ride_id))
    conn.commit()
    cursor.close()
    conn.close()
 
 
def get_active_ride(user_id):
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    cursor.execute("""
        SELECT r.ride_id, r.current_position_index, ro.route_id
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        WHERE (r.passenger_id=%s OR r.driver_id=(SELECT driver_id FROM drivers WHERE user_id=%s))
        AND r.status='active'
        LIMIT 1
    """, (user_id, user_id))
 
    ride = cursor.fetchone()
    cursor.close()
    conn.close()
    return ride