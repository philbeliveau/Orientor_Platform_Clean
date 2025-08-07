#!/usr/bin/env python3
"""
Quick fix script to add clerk_user_id column to users table
Run this once to fix the database schema for Clerk integration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path, override=True)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_clerk_column():
    """Add clerk_user_id column to users table if it doesn't exist"""
    try:
        # Get database URL
        database_url = settings.get_database_url
        engine = create_engine(database_url)
        
        # Check if column exists
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='clerk_user_id';
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(check_sql))
            if result.fetchone():
                print("✅ clerk_user_id column already exists")
                return True
            
            # Add multiple columns for Clerk integration
            columns_to_add = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS clerk_user_id VARCHAR(255) UNIQUE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;"
            ]
            
            for sql in columns_to_add:
                conn.execute(text(sql))
            
            conn.commit()
            print("✅ Successfully added all Clerk integration columns to users table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding clerk_user_id column: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adding clerk_user_id column to users table...")
    success = add_clerk_column()
    sys.exit(0 if success else 1)