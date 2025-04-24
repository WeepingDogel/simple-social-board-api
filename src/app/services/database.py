from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys
import time
import logging
import uuid
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import JSONB

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

logger.info(f"Connecting to database: {DATABASE_URL}")

# Add config for SQLite (using file) or PostgreSQL (using environment variables)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL connection
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Custom UUID type that works with both SQLite and PostgreSQL
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type when using PostgreSQL, 
    uses CHAR for SQLite, storing as string representation.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value)
            except (TypeError, ValueError):
                return None
        return value

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

def init_db():
    """Initialize the database - create tables and enable UUID support for PostgreSQL."""
    if DATABASE_URL.startswith("postgresql"):
        # Create extension if it doesn't exist - for UUID support in PostgreSQL
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Apply database migrations
    apply_migrations()

def apply_migrations():
    """Apply any necessary database migrations."""
    logger.info("Checking and applying database migrations...")
    
    inspector = inspect(engine)
    
    # Add follower_count and following_count columns to user_profiles if they don't exist
    if "user_profiles" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("user_profiles")]
        
        with engine.begin() as conn:
            # Add follower_count if it doesn't exist
            if "follower_count" not in columns:
                logger.info("Adding follower_count column to user_profiles")
                if DATABASE_URL.startswith("postgresql"):
                    conn.execute(text("ALTER TABLE user_profiles ADD COLUMN follower_count INTEGER DEFAULT 0;"))
                else:
                    conn.execute(text("ALTER TABLE user_profiles ADD COLUMN follower_count INTEGER DEFAULT 0;"))
            
            # Add following_count if it doesn't exist
            if "following_count" not in columns:
                logger.info("Adding following_count column to user_profiles")
                if DATABASE_URL.startswith("postgresql"):
                    conn.execute(text("ALTER TABLE user_profiles ADD COLUMN following_count INTEGER DEFAULT 0;"))
                else:
                    conn.execute(text("ALTER TABLE user_profiles ADD COLUMN following_count INTEGER DEFAULT 0;"))
    
    logger.info("Database migrations completed")

# Dependency to get DB session
def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 