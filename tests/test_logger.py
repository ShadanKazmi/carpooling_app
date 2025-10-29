from utils.logger import log_user_activity, log_error, log_db_operation

def test_logging():
    """Test that logs are being created and written to correctly."""
    # Test user activity logging
    log_user_activity("test_user", "test_login", "Testing logger setup")
    
    # Test error logging
    log_error("TestError", "Testing error logging")
    
    # Test database logging
    log_db_operation("SELECT", "users", "success", "Testing DB logging")

if __name__ == "__main__":
    test_logging()
    print("Test complete. Check the logs directory for the following files:")
    print("- logs/user_activity.log")
    print("- logs/errors.log")
    print("- logs/database.log")