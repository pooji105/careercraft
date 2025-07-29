#!/usr/bin/env python3
"""
Initialize the database by creating all tables defined in the SQLAlchemy models.
This script should be run once to set up the database schema.
"""
from app import create_app, db

def init_database():
    """Initialize the database by creating all tables."""
    app = create_app()
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✅ Database tables created successfully!")
        print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()
