#!/usr/bin/env python3
"""
Migration script to add the missing compatibility_vector column to user_profiles table.
This column is needed for the peer matching service.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_compatibility_vector_column():
    """Add the compatibility_vector column to user_profiles table if it doesn't exist."""
    try:
        # Get database URL
        settings = Settings()
        database_url = settings.get_database_url
        logger.info(f"Connecting to database...")
        
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if column already exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'compatibility_vector'
            """)
            
            result = conn.execute(check_column_query)
            column_exists = result.fetchone() is not None
            
            if column_exists:
                logger.info("✅ compatibility_vector column already exists in user_profiles table")
                return True
            
            # Add the column
            logger.info("🔧 Adding compatibility_vector column to user_profiles table...")
            
            add_column_query = text("""
                ALTER TABLE user_profiles 
                ADD COLUMN compatibility_vector JSONB;
            """)
            
            conn.execute(add_column_query)
            conn.commit()
            
            logger.info("✅ Successfully added compatibility_vector column to user_profiles table")
            
            # Verify the column was added
            result = conn.execute(check_column_query)
            if result.fetchone():
                logger.info("✅ Column addition verified")
                return True
            else:
                logger.error("❌ Column verification failed")
                return False
            
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the migration."""
    logger.info("🚀 Starting compatibility_vector column migration...")
    
    success = add_compatibility_vector_column()
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        return 0
    else:
        logger.error("💥 Migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())