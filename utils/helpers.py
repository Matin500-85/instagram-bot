import logging

logger = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    

def user_log(user, message, level='info'):
    user_id = user.id if user else 'Unknown'
    username = f"@{user.username}" if user and user.username else "NoUsername"
    log_msg = f"UserID: {user_id} | Username: {username} | {message}"
    
    if level == 'error':
        logger.error(log_msg)
    else:
        logger.info(log_msg)

