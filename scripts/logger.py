import logging
from datetime import datetime

logging.basicConfig(
    filename="auth_activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
 
def log_user_action(action: str, email: str, role: str = "", success: bool = True, message: str = ""):
    status = "SUCCESS" if success else "FAILURE"
    log_message = f"{action.upper()} - {status} - Email: {email} - Role: {role} - {message}"
    logging.info(log_message)