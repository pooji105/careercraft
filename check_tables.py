from app import create_app, db
from app.models import User

def check_tables():
    app = create_app()
    with app.app_context():
        # Check if users table exists and has required columns
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print("\n=== Database Tables ===")
        for table in tables:
            print(f"\nTable: {table}")
            print("Columns:")
            for column in inspector.get_columns(table):
                print(f"  - {column['name']}: {column['type']} {'(nullable)' if column['nullable'] else '(required)'}")
        
        # Check if we can query the User table
        try:
            user_count = User.query.count()
            print(f"\nNumber of users in database: {user_count}")
        except Exception as e:
            print(f"\nError querying User table: {str(e)}")

if __name__ == '__main__':
    check_tables()
