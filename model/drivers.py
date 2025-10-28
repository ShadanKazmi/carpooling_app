"""
Drivers Model - Database Operations for Drivers
Path: model/drivers.py
Handles CRUD operations and queries for driver table (MySQL compatible)
"""

import sys
sys.path.append('..')
from utils.db_connection import execute_query, execute_update, execute_insert
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# GET DRIVER DETAILS
# ============================================
def get_driver_details(driver_id):
    """
    Fetch driver profile information
    
    Args:
        driver_id (int): The driver ID
    
    Returns:
        dict: Driver details
    """
    try:
        query = """
        SELECT driver_id, name, email, avg_rating, total_rides, 
               created_at, updated_at, is_active
        FROM drivers
        WHERE driver_id = %s
        """
        
        results = execute_query(query, (driver_id,))
        
        if results:
            result = results[0]
            return {
                'driver_id': result['driver_id'],
                'name': result['name'],
                'email': result['email'],
                'avg_rating': result['avg_rating'],
                'total_rides': result['total_rides'],
                'created_at': result['created_at'],
                'updated_at': result['updated_at'],
                'is_active': result['is_active']
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching driver details: {e}")
        return None

# ============================================
# GET DRIVER RIDES
# ============================================
def get_driver_rides(driver_id, status=None, limit=50):
    """
    Fetch rides for a driver
    
    Args:
        driver_id (int): The driver ID
        status (str): Filter by status (optional)
        limit (int): Number of records to fetch
    
    Returns:
        list: List of rides
    """
    try:
        if status:
            query = """
            SELECT r.ride_id, rr.from_city, rr.to_city, r.start_time, 
                   r.status, r.total_fare, p.name as passenger_name, r.seats_booked, rt.distance_km
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            JOIN routes rt ON ro.route_id = rt.route_id
            JOIN passengers p ON r.passenger_id = p.passenger_id
            WHERE r.driver_id = %s AND r.status = %s
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            results = execute_query(query, (driver_id, status, limit))
        else:
            query = """
            SELECT r.ride_id, rr.from_city, rr.to_city, r.start_time, 
                   r.status, r.total_fare, p.name as passenger_name, r.seats_booked, rt.distance_km
            FROM rides r
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            JOIN routes rt ON ro.route_id = rt.route_id
            JOIN passengers p ON r.passenger_id = p.passenger_id
            WHERE r.driver_id = %s
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            results = execute_query(query, (driver_id, limit))
        
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error fetching driver rides: {e}")
        return []

# ============================================
# CREATE DRIVER ACCOUNT
# ============================================
def create_driver(name, email, password):
    """
    Create a new driver account
    
    Args:
        name (str): Driver name
        email (str): Driver email
        password (str): Driver password (will be hashed)
    
    Returns:
        int: Driver ID or None
    """
    try:
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        query = """
        INSERT INTO drivers (name, email, password, is_active)
        VALUES (%s, %s, %s, TRUE)
        """
        
        driver_id = execute_insert(query, (name, email, hashed_password))
        
        if driver_id:
            logger.info(f"✅ Driver created: {driver_id}")
            return driver_id
        else:
            logger.error("❌ Failed to create driver")
            return None
    except Exception as e:
        logger.error(f"❌ Error creating driver: {e}")
        return None

# ============================================
# UPDATE DRIVER TOTAL RIDES
# ============================================
def update_driver_total_rides(driver_id):
    """
    Update total rides count for a driver
    
    Args:
        driver_id (int): The driver ID
    
    Returns:
        bool: Success status
    """
    try:
        query = """
        UPDATE drivers
        SET total_rides = (
            SELECT COUNT(*) FROM rides 
            WHERE driver_id = %s AND status = 'completed'
        )
        WHERE driver_id = %s
        """
        
        affected_rows = execute_update(query, (driver_id, driver_id))
        
        if affected_rows and affected_rows > 0:
            logger.info(f"✅ Total rides updated for driver {driver_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error updating driver total rides: {e}")
        return False

# ============================================
# GET DRIVER STATISTICS
# ============================================
def get_driver_statistics(driver_id):
    """
    Get detailed statistics for a driver
    
    Args:
        driver_id (int): The driver ID
    
    Returns:
        dict: Driver statistics
    """
    try:
        query = """
        SELECT 
            COUNT(*) as total_rides,
            SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) as completed_rides,
            SUM(CASE WHEN r.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_rides,
            SUM(r.total_fare) as total_earnings,
            AVG(rt.distance_km) as avg_distance,
            SUM(rt.distance_km) as total_distance
        FROM rides r
        LEFT JOIN ride_offers ro ON r.offer_id = ro.offer_id
        LEFT JOIN routes rt ON ro.route_id = rt.route_id
        WHERE r.driver_id = %s
        """
        
        results = execute_query(query, (driver_id,))
        
        if results and results[0]['total_rides'] > 0:
            result = results[0]
            return {
                'total_rides': result['total_rides'],
                'completed_rides': result['completed_rides'],
                'cancelled_rides': result['cancelled_rides'],
                'total_earnings': round(result['total_earnings'], 2) if result['total_earnings'] else 0,
                'average_distance': round(result['avg_distance'], 2) if result['avg_distance'] else 0,
                'total_distance': round(result['total_distance'], 2) if result['total_distance'] else 0
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching driver statistics: {e}")
        return None

# ============================================
# GET DRIVER VEHICLE
# ============================================
def get_driver_vehicle(driver_id):
    """
    Fetch vehicle information for a driver
    
    Args:
        driver_id (int): The driver ID
    
    Returns:
        dict: Vehicle details or None
    """
    try:
        query = """
        SELECT vehicle_id, vehicle_name, plate_number, capacity, created_at
        FROM vehicles
        WHERE driver_id = %s
        """
        
        results = execute_query(query, (driver_id,))
        
        if results:
            result = results[0]
            return {
                'vehicle_id': result['vehicle_id'],
                'vehicle_name': result['vehicle_name'],
                'plate_number': result['plate_number'],
                'capacity': result['capacity'],
                'created_at': result['created_at']
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching driver vehicle: {e}")
        return None

# ============================================
# UPDATE DRIVER VEHICLE
# ============================================
def update_driver_vehicle(driver_id, vehicle_name, plate_number, capacity):
    """
    Update driver's vehicle information
    
    Args:
        driver_id (int): The driver ID
        vehicle_name (str): Vehicle name
        plate_number (str): License plate number
        capacity (int): Seating capacity
    
    Returns:
        bool: Success status
    """
    try:
        # Check if vehicle exists
        check_query = "SELECT vehicle_id FROM vehicles WHERE driver_id = %s"
        check_results = execute_query(check_query, (driver_id,))
        
        if check_results:
            # Update existing vehicle
            query_update = """
            UPDATE vehicles
            SET vehicle_name = %s, plate_number = %s, capacity = %s
            WHERE driver_id = %s
            """
            affected_rows = execute_update(query_update, (vehicle_name, plate_number, capacity, driver_id))
        else:
            # Create new vehicle
            query_insert = """
            INSERT INTO vehicles (driver_id, vehicle_name, plate_number, capacity)
            VALUES (%s, %s, %s, %s)
            """
            affected_rows = execute_insert(query_insert, (driver_id, vehicle_name, plate_number, capacity))
        
        if affected_rows:
            logger.info(f"✅ Vehicle updated for driver {driver_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error updating driver vehicle: {e}")
        return False

# ============================================
# SEARCH DRIVERS (ADMIN)
# ============================================
def search_drivers(search_term, limit=20):
    """
    Search for drivers by name or email
    
    Args:
        search_term (str): Search term
        limit (int): Number of results
    
    Returns:
        list: List of drivers
    """
    try:
        query = """
        SELECT driver_id, name, email, avg_rating, total_rides, is_active
        FROM drivers
        WHERE name LIKE %s OR email LIKE %s
        LIMIT %s
        """
        
        search_pattern = f"%{search_term}%"
        results = execute_query(query, (search_pattern, search_pattern, limit))
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error searching drivers: {e}")
        return []

# ============================================
# GET ALL DRIVERS (ADMIN)
# ============================================
def get_all_drivers(limit=100):
    """
    Fetch all drivers (admin use)
    
    Args:
        limit (int): Number of records
    
    Returns:
        list: All drivers
    """
    try:
        query = """
        SELECT driver_id, name, email, avg_rating, total_rides, created_at, is_active
        FROM drivers
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        results = execute_query(query, (limit,))
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error fetching all drivers: {e}")
        return []

# ============================================
# GET ACTIVE DRIVERS (For Ride Offers)
# ============================================
def get_active_drivers(limit=50):
    """
    Get all active drivers available for rides
    
    Args:
        limit (int): Number of drivers to fetch
    
    Returns:
        list: Active drivers
    """
    try:
        query = """
        SELECT d.driver_id, d.name, d.email, d.avg_rating, d.total_rides,
               v.vehicle_name, v.plate_number, v.capacity
        FROM drivers d
        LEFT JOIN vehicles v ON d.driver_id = v.driver_id
        WHERE d.is_active = TRUE
        ORDER BY d.avg_rating DESC
        LIMIT %s
        """
        
        results = execute_query(query, (limit,))
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error fetching active drivers: {e}")
        return []

# ============================================
# UPDATE DRIVER PROFILE
# ============================================
def update_driver_profile(driver_id, name=None, email=None):
    """
    Update driver profile information
    
    Args:
        driver_id (int): The driver ID
        name (str): New name (optional)
        email (str): New email (optional)
    
    Returns:
        bool: Success status
    """
    try:
        if name and email:
            query = """
            UPDATE drivers
            SET name = %s, email = %s, updated_at = NOW()
            WHERE driver_id = %s
            """
            affected_rows = execute_update(query, (name, email, driver_id))
        elif name:
            query = """
            UPDATE drivers
            SET name = %s, updated_at = NOW()
            WHERE driver_id = %s
            """
            affected_rows = execute_update(query, (name, driver_id))
        elif email:
            query = """
            UPDATE drivers
            SET email = %s, updated_at = NOW()
            WHERE driver_id = %s
            """
            affected_rows = execute_update(query, (email, driver_id))
        else:
            logger.warning("❌ No fields to update")
            return False
        
        if affected_rows and affected_rows > 0:
            logger.info(f"✅ Driver {driver_id} profile updated")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error updating driver profile: {e}")
        return False

# ============================================
# DEACTIVATE DRIVER ACCOUNT
# ============================================
def deactivate_driver(driver_id):
    """
    Deactivate a driver account
    
    Args:
        driver_id (int): The driver ID
    
    Returns:
        bool: Success status
    """
    try:
        query = """
        UPDATE drivers
        SET is_active = FALSE, updated_at = NOW()
        WHERE driver_id = %s
        """
        
        affected_rows = execute_update(query, (driver_id,))
        
        if affected_rows and affected_rows > 0:
            logger.info(f"✅ Driver {driver_id} deactivated")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error deactivating driver: {e}")
        return False

# ============================================
# VERIFY DRIVER EMAIL
# ============================================
def verify_driver_email(email):
    """
    Check if driver email exists
    
    Args:
        email (str): Email to verify
    
    Returns:
        bool: True if email exists, False otherwise
    """
    try:
        query = """
        SELECT driver_id FROM drivers WHERE email = %s
        """
        
        results = execute_query(query, (email,))
        return bool(results)
    except Exception as e:
        logger.error(f"❌ Error verifying email: {e}")
        return False

# ============================================
# GET DRIVER EARNINGS
# ============================================
def get_driver_earnings(driver_id, days=30):
    """
    Get driver earnings for a specific period
    
    Args:
        driver_id (int): The driver ID
        days (int): Number of days to look back
    
    Returns:
        dict: Earnings data
    """
    try:
        query = """
        SELECT 
            SUM(r.total_fare) as total_earnings,
            COUNT(r.ride_id) as total_rides,
            AVG(rt.distance_km) as avg_distance
        FROM rides r
        LEFT JOIN ride_offers ro ON r.offer_id = ro.offer_id
        LEFT JOIN routes rt ON ro.route_id = rt.route_id
        WHERE r.driver_id = %s 
        AND r.status = 'completed'
        AND r.start_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        
        results = execute_query(query, (driver_id, days))
        
        if results and results[0]['total_earnings']:
            result = results[0]
            return {
                'total_earnings': round(result['total_earnings'], 2),
                'total_rides': result['total_rides'],
                'average_distance': round(result['avg_distance'], 2) if result['avg_distance'] else 0,
                'period_days': days
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching driver earnings: {e}")
        return None