from flask import Blueprint, render_template
from flask_login import login_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/')
@login_required
def job_tracker():
    return render_template('jobs/tracker.html')

@jobs_bp.route('/applications')
@login_required
def applications():
    return render_template('jobs/applications.html') 