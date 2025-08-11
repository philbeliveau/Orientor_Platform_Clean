#!/usr/bin/env python3
"""
Import Reflection Questions from CSV to Database

This script imports reflection questions from the CSV file into the database
for the strengths_reflection_responses system.
"""

import os
import sys
import csv
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend app to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.models.reflection import Base, ReflectionQuestion

def import_questions():
    """Import reflection questions from CSV to database."""
    print("🚀 Starting reflection questions import...")
    
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
        
        # Read CSV file
        csv_path = Path(__file__).parent.parent / "data" / "Strengths_Reflection_Questions.csv"
        print(f"📖 Reading CSV file: {csv_path}")
        
        if not csv_path.exists():
            print(f"❌ CSV file not found: {csv_path}")
            return False
        
        questions_to_import = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                questions_to_import.append({
                    'id': int(row['id']),
                    'question': row['question'],
                    'category': row['category']
                })
        
        print(f"📊 Found {len(questions_to_import)} questions to import")
        
        # Import questions to database
        with SessionLocal() as db:
            # Check if questions already exist
            existing_count = db.query(ReflectionQuestion).count()
            print(f"🔍 Found {existing_count} existing questions in database")
            
            if existing_count > 0:
                print("⚠️  Questions already exist. Clearing existing data...")
                db.query(ReflectionQuestion).delete()
                db.commit()
            
            # Insert new questions
            print("✅ Inserting questions...")
            for question_data in questions_to_import:
                question = ReflectionQuestion(
                    id=question_data['id'],
                    question=question_data['question'],
                    category=question_data['category']
                )
                db.add(question)
            
            db.commit()
            
            # Verify import
            final_count = db.query(ReflectionQuestion).count()
            print(f"🎉 Successfully imported {final_count} reflection questions!")
            
            # Display sample questions
            print("\n📋 Sample questions:")
            sample_questions = db.query(ReflectionQuestion).limit(3).all()
            for q in sample_questions:
                print(f"  {q.id}. [{q.category}] {q.question[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing questions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = import_questions()
    if success:
        print("\n✅ Import completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Import failed!")
        sys.exit(1)