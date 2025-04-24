import sys
import logging
import time
from .database import wait_for_db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Wait for database to be ready."""
    logger.info("Waiting for database to be ready...")
    max_retries = 60
    retry_interval = 2
    
    for i in range(max_retries):
        if wait_for_db(max_retries=1, retry_interval=1):
            logger.info("Database is ready!")
            return 0
        else:
            logger.info(f"Database not ready yet. Retry {i+1}/{max_retries}...")
            time.sleep(retry_interval)
    
    logger.error(f"Could not connect to database after {max_retries} attempts")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 