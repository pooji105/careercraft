from app import create_app, db
from app.models import User
from sqlalchemy import text

def test_registration():
    app = create_app()
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("[SUCCESS] Database connection successful")
            
            # Check if test user already exists
            existing_user = User.query.filter_by(email="test@example.com").first()
            if existing_user:
                print("[INFO] Test user already exists, deleting...")
                db.session.delete(existing_user)
                db.session.commit()
            
            # Create a test user
            test_user = User(
                name="Test User",
                email="test@example.com",
                current_role="tester"
            )
            test_user.set_password("testpassword123")
            
            # Try to add to database
            db.session.add(test_user)
            db.session.commit()
            print("[SUCCESS] Test user created successfully")
            
            # Verify the user was created
            created_user = User.query.filter_by(email="test@example.com").first()
            if created_user and created_user.check_password("testpassword123"):
                print("[SUCCESS] Test user verified")
            else:
                print("[ERROR] Test user verification failed")
            
            # Clean up
            if created_user:
                db.session.delete(created_user)
                db.session.commit()
                print("[INFO] Test user cleaned up")
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            db.session.rollback()
            raise  # Re-raise the exception to see full traceback

if __name__ == '__main__':
    test_registration()
