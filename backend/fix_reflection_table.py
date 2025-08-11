#!/usr/bin/env python3
"""
Fix reflection table auto-increment issue
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import Base, engine
from app.models.reflection import StrengthsReflectionResponse
from sqlalchemy import text

def fix_reflection_table():
    """Fix the reflection table auto-increment issue"""
    try:
        print("🔧 Fixing strengths_reflection_responses table...")
        
        # First, create all tables to ensure they exist
        print("📋 Creating tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        
        # Check the current sequence and fix it if needed
        with engine.connect() as conn:
            # For PostgreSQL, check if sequence exists and fix it
            print("🔍 Checking sequence configuration...")
            
            # Get the current max ID
            result = conn.execute(text("SELECT COALESCE(MAX(id), 0) FROM strengths_reflection_responses"))
            max_id = result.scalar()
            print(f"📊 Current max ID: {max_id}")
            
            # Check if sequence exists
            seq_check = conn.execute(text("""
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_name = 'strengths_reflection_responses_id_seq'
            """))
            
            if seq_check.fetchone():
                print("✅ Sequence exists, updating sequence value...")
                # Reset sequence to max_id + 1
                next_val = max_id + 1
                conn.execute(text(f"ALTER SEQUENCE strengths_reflection_responses_id_seq RESTART WITH {next_val}"))
                conn.commit()
                print(f"🔄 Sequence reset to start from {next_val}")
            else:
                print("❌ Sequence doesn't exist, creating it...")
                # Create the sequence
                next_val = max_id + 1
                conn.execute(text(f"""
                    CREATE SEQUENCE strengths_reflection_responses_id_seq
                    START WITH {next_val}
                    OWNED BY strengths_reflection_responses.id
                """))
                
                # Set the column default to use the sequence
                conn.execute(text("""
                    ALTER TABLE strengths_reflection_responses 
                    ALTER COLUMN id SET DEFAULT nextval('strengths_reflection_responses_id_seq')
                """))
                conn.commit()
                print(f"✅ Created sequence starting from {next_val}")
            
            # Verify the fix
            print("🧪 Testing insert...")
            test_result = conn.execute(text("SELECT nextval('strengths_reflection_responses_id_seq')"))
            next_id = test_result.scalar()
            print(f"🆔 Next ID will be: {next_id}")
            
        print("✅ Reflection table auto-increment fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing reflection table: {e}")
        return False

if __name__ == "__main__":
    success = fix_reflection_table()
    sys.exit(0 if success else 1)