import pymysql
from pymysql import Error

def setup_database():
    """
    Sets up the carpool_db database and required tables.
    """
    # First connection to create database
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root'
        )
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS carpool_db")
            print("Database 'carpool_db' created or already exists")
            
            # Switch to the database
            cursor.execute("USE carpool_db")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT PRIMARY KEY AUTO_INCREMENT,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    role ENUM('passenger', 'driver', 'both') NOT NULL,
                    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login DATETIME NULL,
                    isActive TINYINT(1) DEFAULT 1,
                    INDEX idx_email (email),
                    INDEX idx_username (username)
                )
            """)
            print("Table 'users' created or already exists")
            
            # Create passengers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passengers (
                    passenger_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    age INT NOT NULL,
                    gender ENUM('male', 'female', 'other') NOT NULL,
                    contact VARCHAR(20) NOT NULL,
                    national_id VARCHAR(50) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_national_id (national_id),
                    CHECK (age >= 18)
                )
            """)
            print("Table 'passengers' created or already exists")
            
            # Create drivers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drivers (
                    driver_id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    age INT NOT NULL,
                    gender ENUM('male', 'female', 'other') NOT NULL,
                    contact VARCHAR(20) NOT NULL,
                    vehicle_no VARCHAR(20) NOT NULL UNIQUE,
                    national_id VARCHAR(50) NOT NULL UNIQUE,
                    route_from VARCHAR(255) NOT NULL,
                    route_to VARCHAR(255) NOT NULL,
                    route_date DATE NOT NULL,
                    route_time TIME NOT NULL,
                    available_seats INT DEFAULT 4,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id),
                    INDEX idx_route (route_from, route_to, route_date),
                    INDEX idx_vehicle_no (vehicle_no),
                    INDEX idx_national_id (national_id),
                    CHECK (age >= 18),
                    CHECK (available_seats >= 0)
                )
            """)
            print("Table 'drivers' created or already exists")
            
            # Create bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INT PRIMARY KEY AUTO_INCREMENT,
                    passenger_id INT NOT NULL,
                    driver_id INT NOT NULL,
                    route_from VARCHAR(255) NOT NULL,
                    route_to VARCHAR(255) NOT NULL,
                    booking_date DATE NOT NULL,
                    booking_time TIME NOT NULL,
                    booking_status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
                    seats_booked INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id) ON DELETE CASCADE,
                    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE,
                    INDEX idx_passenger (passenger_id),
                    INDEX idx_driver (driver_id),
                    INDEX idx_booking_date (booking_date),
                    INDEX idx_status (booking_status),
                    CHECK (seats_booked > 0)
                )
            """)
            print("Table 'bookings' created or already exists")
            
            # Create ratings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    rating_id INT PRIMARY KEY AUTO_INCREMENT,
                    booking_id INT NOT NULL,
                    rated_by INT NOT NULL,
                    rated_user INT NOT NULL,
                    rating DECIMAL(2,1) NOT NULL,
                    review TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
                    FOREIGN KEY (rated_by) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (rated_user) REFERENCES users(user_id) ON DELETE CASCADE,
                    CHECK (rating >= 1.0 AND rating <= 5.0),
                    UNIQUE KEY unique_rating (booking_id, rated_by, rated_user)
                )
            """)
            print("Table 'ratings' created or already exists")
            
            connection.commit()
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error setting up database: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    setup_database()