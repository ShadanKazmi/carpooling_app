"""
Rides Model - Database Operations for Rides
Path: model/rides.py
Handles all CRUD operations for rides table (MySQL compatible)
"""

import sys
sys.path.append('..')
from utils.db_connection import execute_query, execute_update, execute_insert
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# GET ACTIVE RIDE
# ============================================
def get_active_ride(ride_id):
    """
    Fetch an active ride by ID
    
    Args:
        ride_id (int): The ride ID
    
    Returns:
        dict: Ride details or None
    """
    try:
        query = """
        SELECT ride_id, offer_id, passenger_id, driver_id, seats_booked, 
               total_fare, start_time, end_time, status
        FROM rides
        WHERE ride_id = %s AND status IN ('active', 'completed')
        """
        
        results = execute_query(query, (ride_id,))
        
        if results:
            result = results[0]
            return {
                'ride_id': result['ride_id'],
                'offer_id': result['offer_id'],
                'passenger_id': result['passenger_id'],
                'driver_id': result['driver_id'],
                'seats_booked': result['seats_booked'],
                'total_fare': result['total_fare'],
                'start_time': result['start_time'],
                'end_time': result['end_time'],
                'status': result['status']
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching active ride: {e}")
        return None

# ============================================
# GET RIDE DETAILS
# ============================================
def get_ride_details(ride_id):
    """
    Fetch complete ride details with all joined information
    
    Args:
        ride_id (int): The ride ID
    
    Returns:
        dict: Complete ride details
    """
    try:
        query = """
        SELECT 
            r.ride_id, r.status, r.seats_booked, r.total_fare,
            r.start_time, r.end_time,
            rr.from_city, rr.to_city, rt.distance_km,
            p.name as passenger_name, p.email as passenger_email, p.avg_rating as passenger_rating,
            d.name as driver_name, d.email as driver_email, d.avg_rating as driver_rating,
            v.vehicle_name, v.plate_number, v.capacity
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN routes rt ON ro.route_id = rt.route_id
        JOIN passengers p ON r.passenger_id = p.passenger_id
        JOIN drivers d ON r.driver_id = d.driver_id
        JOIN vehicles v ON ro.vehicle_id = v.vehicle_id
        WHERE r.ride_id = %s
        """
        
        results = execute_query(query, (ride_id,))
        
        if results:
            result = results[0]
            return {
                'ride_id': result['ride_id'],
                'status': result['status'],
                'seats_booked': result['seats_booked'],
                'total_fare': result['total_fare'],
                'start_time': result['start_time'],
                'end_time': result['end_time'],
                'from_city': result['from_city'],
                'to_city': result['to_city'],
                'distance_km': result['distance_km'],
                'passenger_name': result['passenger_name'],
                'passenger_email': result['passenger_email'],
                'passenger_rating': result['passenger_rating'],
                'driver_name': result['driver_name'],
                'driver_email': result['driver_email'],
                'driver_rating': result['driver_rating'],
                'vehicle_name': result['vehicle_name'],
                'plate_number': result['plate_number'],
                'vehicle_capacity': result['capacity']
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching ride details: {e}")
        return None

# ============================================
# CREATE RIDE (After Offer Accepted)
# ============================================
def create_ride(offer_id, passenger_id, driver_id, seats_booked, total_fare):
    """
    Create a new ride when offer is accepted
    
    Args:
        offer_id (int): Ride offer ID
        passenger_id (int): Passenger ID
        driver_id (int): Driver ID
        seats_booked (int): Number of seats booked
        total_fare (float): Total fare amount
    
    Returns:
        int: Ride ID or None
    """
    try:
        query = """
        INSERT INTO rides (offer_id, passenger_id, driver_id, seats_booked, total_fare, status)
        VALUES (%s, %s, %s, %s, %s, 'active')
        """
        
        ride_id = execute_insert(query, (offer_id, passenger_id, driver_id, seats_booked, total_fare))
        
        if ride_id:
            logger.info(f"✅ Ride created: {ride_id}")
            return ride_id
        else:
            logger.error("❌ Failed to create ride")
            return None
    except Exception as e:
        logger.error(f"❌ Error creating ride: {e}")
        return None

# ============================================
# UPDATE RIDE STATUS
# ============================================
def update_ride_status(ride_id, new_status):
    """
    Update ride status (active, completed, cancelled)
    
    Args:
        ride_id (int): The ride ID
        new_status (str): New status value
    
    Returns:
        bool: Success status
    """
    valid_statuses = ['active', 'completed', 'cancelled']
    
    if new_status not in valid_statuses:
        logger.warning(f"❌ Invalid status: {new_status}")
        return False
    
    try:
        if new_status == 'completed':
            query = """
            UPDATE rides
            SET status = %s, end_time = NOW()
            WHERE ride_id = %s
            """
        elif new_status == 'active':
            query = """
            UPDATE rides
            SET status = %s, start_time = NOW()
            WHERE ride_id = %s
            """
        else:
            query = """
            UPDATE rides
            SET status = %s
            WHERE ride_id = %s
            """
        
        affected_rows = execute_update(query, (new_status, ride_id))
        
        if affected_rows and affected_rows > 0:
            logger.info(f"✅ Ride {ride_id} status updated to {new_status}")
            return True
        else:
            logger.warning(f"⚠️ No rows updated for ride {ride_id}")
            return False
    except Exception as e:
        logger.error(f"❌ Error updating ride status: {e}")
        return False

# ============================================
# GET RIDES BY PASSENGER
# ============================================
def get_passenger_rides(passenger_id, limit=50):
    """
    Fetch all rides for a passenger
    
    Args:
        passenger_id (int): The passenger ID
        limit (int): Number of records to fetch
    
    Returns:
        list: List of rides
    """
    try:
        query = """
        SELECT r.ride_id, rr.from_city, rr.to_city, r.start_time, 
               r.status, r.total_fare, d.name as driver_name, d.avg_rating, rt.distance_km
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN ride_requests rr ON ro.request_id = rr.request_id
        JOIN routes rt ON ro.route_id = rt.route_id
        JOIN drivers d ON r.driver_id = d.driver_id
        WHERE r.passenger_id = %s
        ORDER BY r.start_time DESC
        LIMIT %s
        """
        
        results = execute_query(query, (passenger_id, limit))
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error fetching passenger rides: {e}")
        return []

# ============================================
# GET RIDES BY DRIVER
# ============================================
def get_driver_rides(driver_id, limit=50):
    """
    Fetch all rides for a driver
    
    Args:
        driver_id (int): The driver ID
        limit (int): Number of records to fetch
    
    Returns:
        list: List of rides
    """
    try:
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
# GET RIDE STATISTICS
# ============================================
def get_ride_stats(ride_id):
    """
    Get detailed statistics for a ride
    
    Args:
        ride_id (int): The ride ID
    
    Returns:
        dict: Ride statistics
    """
    try:
        query = """
        SELECT 
            r.ride_id, r.total_fare, rt.distance_km, 
            TIMESTAMPDIFF(MINUTE, r.start_time, r.end_time) as duration_minutes,
            CASE WHEN r.status = 'completed' THEN TRUE ELSE FALSE END as is_completed
        FROM rides r
        JOIN ride_offers ro ON r.offer_id = ro.offer_id
        JOIN routes rt ON ro.route_id = rt.route_id
        WHERE r.ride_id = %s
        """
        
        results = execute_query(query, (ride_id,))
        
        if results:
            result = results[0]
            distance = result['distance_km'] or 0
            
            return {
                'ride_id': result['ride_id'],
                'total_fare': result['total_fare'],
                'distance_km': distance,
                'duration_minutes': int(result['duration_minutes']) if result['duration_minutes'] else 0,
                'is_completed': result['is_completed'],
                'fare_per_km': result['total_fare'] / distance if distance > 0 else 0
            }
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching ride stats: {e}")
        return None

# ============================================
# GET ALL RIDES (ADMIN)
# ============================================
def get_all_rides(status_filter=None, limit=100):
    """
    Fetch all rides in the system (admin use)
    
    Args:
        status_filter (str): Filter by status (optional)
        limit (int): Number of records to fetch
    
    Returns:
        list: List of all rides
    """
    try:
        if status_filter:
            query = """
            SELECT r.ride_id, p.name as passenger_name, d.name as driver_name, 
                   rr.from_city, rr.to_city, r.total_fare, r.status, r.start_time
            FROM rides r
            JOIN passengers p ON r.passenger_id = p.passenger_id
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            WHERE r.status = %s
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            results = execute_query(query, (status_filter, limit))
        else:
            query = """
            SELECT r.ride_id, p.name as passenger_name, d.name as driver_name, 
                   rr.from_city, rr.to_city, r.total_fare, r.status, r.start_time
            FROM rides r
            JOIN passengers p ON r.passenger_id = p.passenger_id
            JOIN drivers d ON r.driver_id = d.driver_id
            JOIN ride_offers ro ON r.offer_id = ro.offer_id
            JOIN ride_requests rr ON ro.request_id = rr.request_id
            ORDER BY r.start_time DESC
            LIMIT %s
            """
            results = execute_query(query, (limit,))
        
        return results if results else []
    except Exception as e:
        logger.error(f"❌ Error fetching all rides: {e}")
        return []

# ============================================
# GET RIDE COUNT BY STATUS
# ============================================
def get_ride_count_by_status():
    """
    Get count of rides grouped by status
    
    Returns:
        dict: Ride counts by status
    """
    try:
        query = """
        SELECT status, COUNT(*) as count
        FROM rides
        GROUP BY status
        """
        
        results = execute_query(query)
        
        if results:
            counts = {}
            for row in results:
                counts[row['status']] = row['count']
            return counts
        return {}
    except Exception as e:
        logger.error(f"❌ Error fetching ride counts: {e}")
        return {}

# ============================================
# GET TOTAL REVENUE
# ============================================
def get_total_revenue():
    """
    Get total revenue from all completed rides
    
    Returns:
        float: Total revenue amount
    """
    try:
        query = """
        SELECT SUM(total_fare) as total
        FROM rides
        WHERE status = 'completed'
        """
        
        results = execute_query(query)
        
        if results and results[0]['total']:
            return float(results[0]['total'])
        return 0.0
    except Exception as e:
        logger.error(f"❌ Error fetching total revenue: {e}")
        return 0.0