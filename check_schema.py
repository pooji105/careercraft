from app import create_app, db
from app.models import InterviewFeedback

def check_schema():
    app = create_app()
    with app.app_context():
        # Get table information
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('interview_feedback')
        
        print("\nColumns in interview_feedback table:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
        
        # Check if our required columns exist
        required_columns = {'questions_json', 'feedback_json', 'question', 'answer', 'feedback'}
        existing_columns = {col['name'] for col in columns}
        
        print("\nStatus:")
        for col in required_columns:
            status = "✅ Found" if col in existing_columns else "❌ Missing"
            print(f"{status} column: {col}")
        
        # Check if we can create a test record
        try:
            test_feedback = InterviewFeedback(
                question="Test question",
                answer="Test answer",
                feedback="Test feedback",
                questions_json='{"question": "test"}',
                feedback_json='{"feedback": "test"}'
            )
            db.session.add(test_feedback)
            db.session.commit()
            print("\n✅ Successfully created test record")
            
            # Clean up
            db.session.delete(test_feedback)
            db.session.commit()
            print("✅ Successfully cleaned up test record")
            
        except Exception as e:
            print(f"\n❌ Error creating test record: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    check_schema()
