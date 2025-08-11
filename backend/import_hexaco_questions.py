#!/usr/bin/env python3
"""
Import HEXACO Questions from CSV to Database

This script imports HEXACO personality test questions from CSV files into the database
for the hexaco_questions table.
"""

import os
import sys
import csv
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.models.reflection import Base, HexacoQuestion

def import_hexaco_questions():
    """Import HEXACO questions from CSV files to database."""
    print("🚀 Starting HEXACO questions import...")
    
    try:
        # Get database connection
        database_url = os.getenv("DATABASE_URL") or os.getenv("RAILWAY_DATABASE_URL")
        if not database_url:
            print("❌ No database URL found in environment variables")
            return False
            
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables if they don't exist
        print("📋 Creating tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        
        # Find CSV files
        data_dir = Path(__file__).parent.parent / "data" / "HEXACO"
        csv_files = [
            data_dir / "English_60_FULL.csv",
            data_dir / "English_100_FULL.csv", 
            data_dir / "French_60_FULL.csv",
            data_dir / "French_100_FULL.csv"
        ]
        
        all_questions = []
        
        for csv_file in csv_files:
            if not csv_file.exists():
                print(f"⚠️  CSV file not found: {csv_file}")
                continue
                
            print(f"📖 Reading {csv_file.name}...")
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                file_questions = []
                
                for row in reader:
                    question = HexacoQuestion(
                        item_id=int(row['item_id']),
                        item_text=row['item_text'],
                        response_min=int(row['response_min']),
                        response_max=int(row['response_max']),
                        version=row['version'],
                        language=row['language'],
                        reverse_keyed=row['reverse_keyed'].lower() == 'true',
                        facet=row['facet']
                    )
                    file_questions.append(question)
                
                print(f"   📊 Found {len(file_questions)} questions")
                all_questions.extend(file_questions)
        
        print(f"\n📈 Total questions to import: {len(all_questions)}")
        
        # Import to database
        with SessionLocal() as db:
            # Check if questions already exist
            existing_count = db.query(HexacoQuestion).count()
            print(f"🔍 Found {existing_count} existing HEXACO questions in database")
            
            if existing_count > 0:
                print("⚠️  HEXACO questions already exist. Clearing existing data...")
                db.query(HexacoQuestion).delete()
                db.commit()
            
            # Insert new questions
            print("✅ Inserting questions...")
            db.add_all(all_questions)
            db.commit()
            
            # Verify import
            final_count = db.query(HexacoQuestion).count()
            print(f"🎉 Successfully imported {final_count} HEXACO questions!")
            
            # Display sample questions by version
            print("\n📋 Sample questions by version:")
            versions = db.query(HexacoQuestion.version).distinct().all()
            for version in versions:
                version_name = version[0]
                sample_questions = db.query(HexacoQuestion).filter(
                    HexacoQuestion.version == version_name
                ).limit(2).all()
                
                print(f"\n  📝 {version_name}:")
                for q in sample_questions:
                    print(f"    {q.item_id}. [{q.facet}] {q.item_text[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing HEXACO questions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_hexaco_questions()
    if success:
        print("\n✅ HEXACO questions import completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ HEXACO questions import failed!")
        sys.exit(1)