from app import create_app, db
from app.models import User, Resume, UploadedResume, JobApplication, Skill, InterviewFeedback, JobMatch, JobMatchHistory

def reset_database():
    app = create_app()
    with app.app_context():
        print("Dropping all database tables...")
        db.drop_all()
        print("Creating all database tables...")
        db.create_all()
        print("Database reset complete!")

if __name__ == '__main__':
    reset_database()
