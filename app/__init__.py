from flask import Flask
from dotenv import load_dotenv
import os

# Import extensions
from app.extensions import db, migrate, login_manager, csrf

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///careercraft.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.resume import resume_bp
    from app.routes.interview import interview_bp
    from app.routes.jobs import jobs_bp
    from app.routes.skills import skills_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(resume_bp)  # No url_prefix so /resume-builder works
    app.register_blueprint(interview_bp, url_prefix='/interview')
    app.register_blueprint(jobs_bp)  # No url_prefix for job tracker
    app.register_blueprint(skills_bp, url_prefix='/skills')
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import User
    
    # Register custom Jinja2 filters
    import json
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string to Python object"""
        if not value:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    
    return app