from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Resume, JobApplication, Skill

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    total_resumes = Resume.query.filter_by(user_id=current_user.id).count()
    total_applications = JobApplication.query.filter_by(user_id=current_user.id).count()
    total_skills = Skill.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard/index.html', total_resumes=total_resumes, total_applications=total_applications, total_skills=total_skills) 