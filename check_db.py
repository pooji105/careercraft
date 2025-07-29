from app import create_app, db
from app.models import InterviewFeedback

app = create_app()

with app.app_context():
    # Check if table exists
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('interview_feedback')]
    print("Columns in interview_feedback table:", columns)
    
    # Check migration version
    from flask_migrate import current
    print("\nCurrent migration version:", current())
