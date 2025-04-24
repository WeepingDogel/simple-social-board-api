import os
import sys
import logging
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adjust the import path for both Docker and local environments
try:
    # First try direct import (for when PYTHONPATH is set correctly)
    from src.app.services.database import engine, SessionLocal
    from src.app.models.model import Base, UserProfile, User
except ImportError:
    # Fallback for local development
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.services.database import engine, SessionLocal
    from app.models.model import Base, UserProfile, User

def run_migration():
    """Run database migrations for user profiles table."""
    logger.info("Starting user profile migration...")
    
    try:
        inspector = inspect(engine)
        
        # Check if user_profiles table exists, if not create all tables
        if "user_profiles" not in inspector.get_table_names():
            logger.info("user_profiles table does not exist. Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        
        # Now check for our specific columns
        columns = [col["name"] for col in inspector.get_columns("user_profiles")]
        
        with engine.begin() as conn:
            # Add follower_count column if it doesn't exist
            if "follower_count" not in columns:
                logger.info("Adding follower_count column to user_profiles")
                conn.execute(text("ALTER TABLE user_profiles ADD COLUMN follower_count INTEGER DEFAULT 0;"))
                logger.info("follower_count column added successfully")
            else:
                logger.info("follower_count column already exists")
            
            # Add following_count column if it doesn't exist
            if "following_count" not in columns:
                logger.info("Adding following_count column to user_profiles")
                conn.execute(text("ALTER TABLE user_profiles ADD COLUMN following_count INTEGER DEFAULT 0;"))
                logger.info("following_count column added successfully")
            else:
                logger.info("following_count column already exists")
            
        logger.info("Migration completed successfully")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        logger.info("Migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Migration failed")
        sys.exit(1) 