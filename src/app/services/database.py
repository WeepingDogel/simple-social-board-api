from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL can be set as an environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./social_board.db")

logger.info(f"Connecting to database: {DATABASE_URL}")

# Create engine with proper connection parameters
if DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL, enable appropriate connection settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=300,    # Recycle connections after 5 minutes
        echo=True            # Log SQL queries during development
    )
else:
    # SQLite or other database
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def wait_for_db(max_retries=10, retry_interval=2):
    """Wait for database to be available"""
    logger.info("Waiting for database to be ready...")
    retries = 0
    
    while retries < max_retries:
        try:
            # Try to connect and execute a simple query
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("Database connection successful!")
                return True
        except Exception as e:
            retries += 1
            logger.warning(f"Database connection attempt {retries}/{max_retries} failed: {e}")
            if retries >= max_retries:
                logger.error(f"Could not connect to database after {max_retries} attempts")
                return False
            time.sleep(retry_interval)
    
    return False

# Create tables function
def init_db():
    """Initialize the database - create tables if they don't exist"""
    # First, wait for database to be available
    if not wait_for_db():
        logger.error("Database is not available, exiting")
        sys.exit(1)
    
    try:
        # Import models here to avoid circular imports
        from ..models.model import User, UserProfile, Post, PostImage, Like, Repost, MediaFile, ModerationAction
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {tables}")
        
        if "users" not in tables:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            
            # Verify tables were created
            new_tables = inspect(engine).get_table_names()
            logger.info(f"Tables after creation: {new_tables}")
            
            if "users" not in new_tables:
                logger.error("Failed to create tables properly")
                sys.exit(1)
        else:
            logger.info("Tables already exist, skipping creation")
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        sys.exit(1)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 