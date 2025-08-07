#!/usr/bin/env python3
"""
Add remaining columns needed for Clerk integration
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

def add_remaining_columns():
    """Add first_name, last_name, is_active columns"""
    try:
        database_url = settings.get_database_url
        engine = create_engine(database_url)
        
        # Add the missing columns
        columns_to_add = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);", 
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;"
        ]
        
        with engine.connect() as conn:
            for sql in columns_to_add:
                try:
                    conn.execute(text(sql))
                    print(f"✅ Executed: {sql}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"ℹ️ Column already exists: {sql}")
                    else:
                        print(f"❌ Error with {sql}: {e}")
            
            conn.commit()
            print("✅ All remaining columns added successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error adding columns: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Adding remaining Clerk integration columns...")
    success = add_remaining_columns()
    sys.exit(0 if success else 1)