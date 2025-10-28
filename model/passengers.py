"""
Passengers Model - Database Operations for Passengers
Path: model/passengers.py
Handles CRUD operations and queries for passenger table
"""

from utils.db_connection import get_db_connection
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# GET PASSENGER DETAILS
# ============================================
def get_passenger_details(passenger_id):
    """
    Fetch passenger profile information
    
    Args:
        passenger_id (int): The passenger ID
    
    Returns:
        dict: Passenger details
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT passenger_id, name, email, avg_rating, total_rides, 
               created_at, updated_at, is_active
        FROM passengers
        WHERE passenger_id = %s
        """
        
        cursor.execute(query, (passenger_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'passenger_id': result[0],
                'name': result[1],
                'email': result[2],
                'avg_rating': result[3],
                'total_rides': result[4],
                'created_at': result[5],
                'updated_at': result[6],
                'is_active': result[7]
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching passenger details: {e}")
        return None

# ============================================
# GET PASSENGER RIDES
# ============================================
def get_passenger_rides(passenger_id, status=None, limit=50):
    """
    Fetch rides for a passenger
    
    Args:
        passenger_id (int): The passenger ID
        status (str): Filter by status (optional)
        limit (int): Number of records to fetch
    
    Returns:
        list: List of rides
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if status:
            query = """
            SELECT r.ride_id, rr.from_city, rr.to_city, r.start_time, 
                   r.status, r.total_fare, d.name, d.avg_rating, rt.distance_km
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            JOIN routes rt ON ro.route_id = rt.route_id
            JOIN drivers d ON r.driver_id = d.driver_id
            WHERE r.passenger_id = %s AND r.status = %s
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            cursor.execute(query, (passenger_id, status, limit))
        else:
            query = """
            SELECT r.ride_id, rr.from_city, rr.to_city, r.start_time, 
                   r.status, r.total_fare, d.name, d.avg_rating, rt.distance_km
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            JOIN routes rt ON ro.route_id = rt.route_id
            JOIN drivers d ON r.driver_id = d.driver_id
            WHERE r.passenger_id = %s
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            cursor.execute(query, (passenger_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error fetching passenger rides: {e}")
        return []

# ============================================
# CREATE PASSENGER ACCOUNT
# ============================================
def create_passenger(name, email, password):
    """
    Create a new passenger account
    
    Args:
        name (str): Passenger name
        email (str): Passenger email
        password (str): Passenger password (will be hashed)
    
    Returns:
        int: Passenger ID or None
    """
    try:
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO passengers (name, email, password, is_active)
        VALUES (%s, %s, %s, TRUE)
        RETURNING passenger_id
        """
        
        cursor.execute(query, (name, email, hashed_password))
        passenger_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        logger.info(f"Passenger created: {passenger_id}")
        return passenger_id
    except Exception as e:
        logger.error(f"Error creating passenger: {e}")
        return None

# ============================================
# UPDATE PASSENGER TOTAL RIDES
# ============================================
def update_passenger_total_rides(passenger_id):
    """
    Update total rides count for a passenger
    
    Args:
        passenger_id (int): The passenger ID
    
    Returns:
        bool: Success status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE passengers
        SET total_rides = (
            SELECT COUNT(*) FROM rides 
            WHERE passenger_id = %s AND status = 'completed'
        )
        WHERE passenger_id = %s
        """
        
        cursor.execute(query, (passenger_id, passenger_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Total rides updated for passenger {passenger_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating passenger total rides: {e}")
        return False

# ============================================
# GET PASSENGER STATISTICS
# ============================================
def get_passenger_statistics(passenger_id):
    """
    Get detailed statistics for a passenger
    
    Args:
        passenger_id (int): The passenger ID
    
    Returns:
        dict: Passenger statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            COUNT(*) as total_rides,
            SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) as completed_rides,
            SUM(CASE WHEN r.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_rides,
            SUM(r.total_fare) as total_spent,
            AVG(rt.distance_km) as avg_distance
        FROM rides r
        LEFT JOIN ride_offers ro ON r.offer_id = ro.offer_id
        LEFT JOIN routes rt ON ro.route_id = rt.route_id
        WHERE r.passenger_id = %s
        """
        
        cursor.execute(query, (passenger_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                'total_rides': result[0],
                'completed_rides': result[1],
                'cancelled_rides': result[2],
                'total_spent': result[3],
                'average_distance': round(result[4], 2) if result[4] else 0
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching passenger statistics: {e}")
        return None

# ============================================
# SEARCH PASSENGERS (ADMIN)
# ============================================
def search_passengers(search_term, limit=20):
    """
    Search for passengers by name or email
    
    Args:
        search_term (str): Search term
        limit (int): Number of results
    
    Returns:
        list: List of passengers
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT passenger_id, name, email, avg_rating, total_rides, is_active
        FROM passengers
        WHERE name ILIKE %s OR email ILIKE %s
        LIMIT %s
        """
        
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern, limit))
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Error searching passengers: {e}")
        return []

# ============================================
# GET ALL PASSENGERS (ADMIN)
# ============================================
def get_all_passengers(limit=100):
    """
    Fetch all passengers (admin use)
    
    Args:
        limit (int): Number of records
    
    Returns:
        list: All passengers
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT passenger_id, name, email, avg_rating, total_rides, created_at, is_active
        FROM passengers
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Error fetching all passengers: {e}")
        return []