import logging
import os
from datetime import datetime
from functools import wraps
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure different loggers for different types of activities
def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup a specific logger with rotating file handler"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create a rotating file handler
    handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, log_file),
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    handler.setLevel(level)
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger if it doesn't already have it
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Setup different loggers for different activities
auth_logger = setup_logger('auth', 'auth.log')
ride_logger = setup_logger('rides', 'rides.log')
user_logger = setup_logger('user_activity', 'user_activity.log')
error_logger = setup_logger('errors', 'errors.log', level=logging.ERROR)
db_logger = setup_logger('database', 'database.log')

def log_activity(activity_type="general"):
    """
    Decorator to log function calls with their arguments and results
    
    Usage:
    @log_activity("auth")
    def some_function(arg1, arg2):
        pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(activity_type)
            
            # Log function call
            func_args = ", ".join([
                *[str(arg) for arg in args],
                *[f"{k}={v}" for k, v in kwargs.items()]
            ])
            logger.info(f"Called {func.__name__} with args: {func_args}")
            
            try:
                result = func(*args, **kwargs)
                # Log success
                logger.info(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                # Log error
                error_logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator

# Function to log user activities
def log_user_activity(user_id, activity, details=None):
    """
    Log user activities with details
    
    Args:
        user_id: ID of the user performing the action
        activity: Type of activity (e.g., 'login', 'logout', 'request_ride')
        details: Additional details about the activity
    """
    message = f"User {user_id} - {activity}"
    if details:
        message += f" - {details}"
    user_logger.info(message)

# Function to log database operations
def log_db_operation(operation, table, status, details=None):
    """
    Log database operations
    
    Args:
        operation: Type of operation (e.g., 'INSERT', 'UPDATE', 'DELETE')
        table: Name of the table being operated on
        status: Status of the operation ('success' or 'failed')
        details: Additional details about the operation
    """
    message = f"{operation} on {table} - {status}"
    if details:
        message += f" - {details}"
    db_logger.info(message)

# Function to log errors
def log_error(error_type, error_message, stack_trace=None):
    """
    Log errors with stack trace
    
    Args:
        error_type: Type of error
        error_message: Error message
        stack_trace: Stack trace if available
    """
    message = f"{error_type}: {error_message}"
    if stack_trace:
        message += f"\nStack trace: {stack_trace}"
    error_logger.error(message)