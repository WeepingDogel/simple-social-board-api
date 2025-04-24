#!/usr/bin/env python3
import os
import sys
import time
import logging
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database import engine, Base, wait_for_db
from app.models.model import User, UserProfile, Post, PostImage, Like, Repost, MediaFile, ModerationAction

def create_tables_manually():
    """Create tables using direct SQL commands"""
    logger.info("Creating tables using direct SQL...")
    
    with engine.connect() as connection:
        # Create users table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR NOT NULL UNIQUE,
            username VARCHAR NOT NULL UNIQUE,
            hashed_password VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create user_profiles table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id),
            display_name VARCHAR,
            avatar_url VARCHAR,
            background_color VARCHAR DEFAULT '#ffffff',
            bio VARCHAR(160),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create posts table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            content VARCHAR(4000) NOT NULL,
            author_id INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            like_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            original_post_id INTEGER REFERENCES posts(id)
        )
        """))
        
        # Create post_images table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS post_images (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL REFERENCES posts(id),
            image_url VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create likes table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS likes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            post_id INTEGER NOT NULL REFERENCES posts(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_user_post_like UNIQUE (user_id, post_id)
        )
        """))
        
        # Create reposts table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS reposts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            post_id INTEGER NOT NULL REFERENCES posts(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_user_post_repost UNIQUE (user_id, post_id)
        )
        """))
        
        # Create media_files table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS media_files (
            id SERIAL PRIMARY KEY,
            filename VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            file_url VARCHAR NOT NULL,
            mime_type VARCHAR NOT NULL,
            file_size INTEGER NOT NULL,
            uploader_id INTEGER NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Create moderation_actions table
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS moderation_actions (
            id SERIAL PRIMARY KEY,
            admin_id INTEGER NOT NULL REFERENCES users(id),
            action_type VARCHAR NOT NULL,
            target_user_id INTEGER REFERENCES users(id),
            target_post_id INTEGER REFERENCES posts(id),
            reason VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        
        # Commit the transaction
        connection.commit()
    
    logger.info("All tables created successfully with direct SQL!")

def initialize_database():
    """Initialize the database by creating all tables"""
    if not wait_for_db(max_retries=30, retry_interval=1):
        logger.error("Could not connect to the database")
        sys.exit(1)
        
    try:
        # Try SQLAlchemy's way first
        logger.info("Creating all database tables with SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        logger.info("SQLAlchemy table creation completed")
        
        # Verify tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database after SQLAlchemy creation: {tables}")
        
        required_tables = [
            "users", "user_profiles", "posts", "post_images", 
            "likes", "reposts", "media_files", "moderation_actions"
        ]
        
        missing = [table for table in required_tables if table not in tables]
        if missing:
            logger.warning(f"Some tables not created by SQLAlchemy: {missing}")
            # Fall back to direct SQL creation
            create_tables_manually()
            
            # Verify again
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Tables in database after direct SQL creation: {tables}")
            
            missing = [table for table in required_tables if table not in tables]
            if missing:
                logger.error(f"Still failed to create some tables: {missing}")
                sys.exit(1)
        
        logger.info("All required tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating tables with SQLAlchemy: {e}")
        logger.info("Falling back to direct SQL creation")
        try:
            create_tables_manually()
            return True
        except Exception as e2:
            logger.error(f"Error creating tables with direct SQL: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    initialize_database() 