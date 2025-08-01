#!/usr/bin/env python3
"""
Test script to verify Skill Tracker functionality with renamed table
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    from app.models import Skill
    from app.extensions import db
    
    print("✓ Creating Flask app...")
    app = create_app()
    
    with app.app_context():
        # Test the Skill model
        print(f"✓ Skill model table name: {Skill.__tablename__}")
        
        # Test database connection
        try:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT COUNT(*) FROM skill_tracker")).scalar()
            print(f"✓ skill_tracker table exists with {result} records")
            
            # Test if we can query the Skill model
            skills_count = Skill.query.count()
            print(f"✓ Skill model query successful: {skills_count} skills found")
            
            print("✓ All tests passed! Skill Tracker is working correctly with the renamed table.")
            
        except Exception as e:
            print(f"✗ Database error: {e}")
            sys.exit(1)
            
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1) 