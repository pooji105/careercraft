from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app.models import Resume, JobApplication, Skill

dashboard_bp = Blueprint('dashboard', __name__)

def safe_count(query):
    try:
        return query.count()
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in dashboard: {str(e)}")
        return 0

@dashboard_bp.route('/')
@login_required
def dashboard():
    try:
        # Get counts with error handling
        total_resumes = safe_count(Resume.query.filter_by(user_id=current_user.id))
        total_applications = safe_count(JobApplication.query.filter_by(user_id=current_user.id))
        total_skills = safe_count(Skill.query.filter_by(user_id=current_user.id))
        
        return render_template(
            'dashboard/index.html',
            total_resumes=total_resumes,
            total_applications=total_applications,
            total_skills=total_skills
        )
    except Exception as e:
        current_app.logger.error(f"Error in dashboard route: {str(e)}")
        # Provide default values if there's an error
        return render_template(
            'dashboard/index.html',
            total_resumes=0,
            total_applications=0,
            total_skills=0
        )