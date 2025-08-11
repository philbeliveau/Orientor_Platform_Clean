#!/usr/bin/env python3
"""
Initialize reflection table with proper sequence
This should be run once to fix the database table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import Base, get_db, SessionLocal
from app.models.reflection import StrengthsReflectionResponse
from sqlalchemy import create_engine, text
from app.core.config import settings

def init_reflection_table():
    """Initialize the reflection table with proper auto-increment"""
    try:
        print("🔧 Initializing reflection table...")
        
        # Get database session
        db = SessionLocal()
        
        if db is None:
            print("❌ Could not get database session")
            return False
            
        try:
            # First, ensure the table exists
            Base.metadata.create_all(bind=db.bind)
            print("✅ Tables created/verified")
            
            # Check if sequence exists and create it if needed
            try:
                # Try to get next value from sequence
                result = db.execute(text("SELECT nextval('strengths_reflection_responses_id_seq')"))
                next_id = result.scalar()
                print(f"✅ Sequence exists, next ID: {next_id}")
                
                # Reset the sequence to avoid conflicts
                max_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM strengths_reflection_responses"))
                max_id = max_result.scalar()
                
                if next_id <= max_id:
                    # Reset sequence to proper value
                    new_next = max_id + 1
                    db.execute(text(f"SELECT setval('strengths_reflection_responses_id_seq', {new_next}, false)"))
                    db.commit()
                    print(f"🔄 Sequence reset to {new_next}")
                    
            except Exception as seq_error:
                if "does not exist" in str(seq_error):
                    print("⚠️ Sequence doesn't exist, creating it...")
                    
                    # Get current max ID
                    max_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM strengths_reflection_responses"))
                    max_id = max_result.scalar()
                    start_val = max_id + 1
                    
                    # Create sequence
                    db.execute(text(f"""
                        CREATE SEQUENCE strengths_reflection_responses_id_seq
                        START WITH {start_val}
                        INCREMENT BY 1
                        NO MINVALUE
                        NO MAXVALUE
                        CACHE 1
                    """))
                    
                    # Set column default
                    db.execute(text("""
                        ALTER TABLE strengths_reflection_responses 
                        ALTER COLUMN id SET DEFAULT nextval('strengths_reflection_responses_id_seq')
                    """))
                    
                    # Set ownership
                    db.execute(text("""
                        ALTER SEQUENCE strengths_reflection_responses_id_seq 
                        OWNED BY strengths_reflection_responses.id
                    """))
                    
                    db.commit()
                    print(f"✅ Created sequence starting from {start_val}")
                else:
                    raise seq_error
            
            print("✅ Reflection table initialization completed!")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error initializing reflection table: {e}")
        return False

if __name__ == "__main__":
    success = init_reflection_table()
    sys.exit(0 if success else 1)