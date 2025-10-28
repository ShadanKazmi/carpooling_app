"""
Ratings Model - Database Operations for Ratings
Path: model/ratings.py
Handles all rating operations and feedback management
"""

from utils.db_connection import get_db_connection
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# SUBMIT RATING
# ============================================
def submit_rating(ride_id, rated_by, rated_user, rating, feedback=""):
    """
    Submit a rating for a ride
    
    Args:
        ride_id (int): The ride ID
        rated_by (int): User ID giving the rating
        rated_user (int): User ID being rated
        rating (float): Rating value (0-5)
        feedback (str): Optional feedback text
    
    Returns:
        bool: Success status
    """
    if not (0 <= rating <= 5):
        logger.warning(f"Invalid rating value: {rating}")
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO ratings (ride_id, rated_by, rated_user, rating, feedback)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING rating_id
        """
        
        cursor.execute(query, (ride_id, rated_by, rated_user, rating, feedback))
        rating_id = cursor.fetchone()[0]
        conn.commit()
        
        # Update average rating for the user being rated
        update_average_rating(rated_user)
        
        conn.close()
        logger.info(f"Rating {rating_id} submitted for user {rated_user}")
        return True
    except Exception as e:
        logger.error(f"Error submitting rating: {e}")
        return False

# ============================================
# UPDATE AVERAGE RATING
# ============================================
def update_average_rating(user_id, is_driver=None):
    """
    Update average rating for a user
    
    Args:
        user_id (int): The user ID
        is_driver (bool): Whether user is driver or passenger (auto-detect if None)
    
    Returns:
        bool: Success status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate average rating
        query_avg = """
        SELECT AVG(rating) FROM ratings WHERE rated_user = %s
        """
        cursor.execute(query_avg, (user_id,))
        avg_rating = cursor.fetchone()[0] or 0
        
        # Determine if driver or passenger
        if is_driver is None:
            cursor.execute("SELECT COUNT(*) FROM drivers WHERE driver_id = %s", (user_id,))
            is_driver = cursor.fetchone()[0] > 0
        
        # Update the user record
        if is_driver:
            query_update = """
            UPDATE drivers SET avg_rating = %s WHERE driver_id = %s
            """
        else:
            query_update = """
            UPDATE passengers SET avg_rating = %s WHERE passenger_id = %s
            """
        
        cursor.execute(query_update, (avg_rating, user_id))
        conn.commit()
        conn.close()
        
        logger.info(f"Average rating updated for user {user_id}: {avg_rating:.2f}")
        return True
    except Exception as e:
        logger.error(f"Error updating average rating: {e}")
        return False

# ============================================
# GET RIDE RATING
# ============================================
def get_ride_rating(ride_id):
    """
    Get rating information for a ride
    
    Args:
        ride_id (int): The ride ID
    
    Returns:
        dict: Rating details or None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT rating_id, ride_id, rated_by, rated_user, rating, feedback, created_at
        FROM ratings
        WHERE ride_id = %s
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (ride_id,))
        results = cursor.fetchall()
        conn.close()
        
        if results:
            ratings_list = []
            for row in results:
                ratings_list.append({
                    'rating_id': row[0],
                    'ride_id': row[1],
                    'rated_by': row[2],
                    'rated_user': row[3],
                    'rating': row[4],
                    'feedback': row[5],
                    'created_at': row[6]
                })
            return ratings_list
        return None
    except Exception as e:
        logger.error(f"Error fetching ride rating: {e}")
        return None

# ============================================
# GET USER RATINGS
# ============================================
def get_user_ratings(user_id, limit=20):
    """
    Get all ratings for a user
    
    Args:
        user_id (int): The user ID
        limit (int): Number of records to fetch
    
    Returns:
        list: List of ratings
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT rating_id, ride_id, rated_by, rating, feedback, created_at
        FROM ratings
        WHERE rated_user = %s
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Error fetching user ratings: {e}")
        return []

# ============================================
# GET RATING STATISTICS
# ============================================
def get_rating_statistics(user_id):
    """
    Get rating statistics for a user
    
    Args:
        user_id (int): The user ID
    
    Returns:
        dict: Rating statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            AVG(rating) as avg_rating,
            COUNT(*) as total_ratings,
            MIN(rating) as min_rating,
            MAX(rating) as max_rating,
            SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) as positive_ratings
        FROM ratings
        WHERE rated_user = %s
        """
        
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[1] > 0:  # If ratings exist
            return {
                'average_rating': round(result[0], 2),
                'total_ratings': result[1],
                'min_rating': result[2],
                'max_rating': result[3],
                'positive_ratings': result[4],
                'positive_percentage': round((result[4] / result[1]) * 100, 1)
            }
        return None
    except Exception as e:
        logger.error(f"Error fetching rating statistics: {e}")
        return None

# ============================================
# DELETE RATING (ADMIN)
# ============================================
def delete_rating(rating_id):
    """
    Delete a rating (admin function)
    
    Args:
        rating_id (int): The rating ID
    
    Returns:
        bool: Success status
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get rated_user before deletion
        query_select = "SELECT rated_user FROM ratings WHERE rating_id = %s"
        cursor.execute(query_select, (rating_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
        
        rated_user = result[0]
        
        # Delete rating
        query_delete = "DELETE FROM ratings WHERE rating_id = %s"
        cursor.execute(query_delete, (rating_id,))
        conn.commit()
        
        # Recalculate average rating
        update_average_rating(rated_user)
        
        conn.close()
        logger.info(f"Rating {rating_id} deleted")
        return True
    except Exception as e:
        logger.error(f"Error deleting rating: {e}")
        return False

# ============================================
# CHECK IF RATED
# ============================================
def check_if_rated(ride_id, rated_by):
    """
    Check if a user has already rated a ride
    
    Args:
        ride_id (int): The ride ID
        rated_by (int): The user ID
    
    Returns:
        bool: True if already rated, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) FROM ratings
        WHERE ride_id = %s AND rated_by = %s
        """
        
        cursor.execute(query, (ride_id, rated_by))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    except Exception as e:
        logger.error(f"Error checking rating status: {e}")
        return False