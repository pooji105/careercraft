from flask import Blueprint, render_template
from flask_login import login_required

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/')
@login_required
def interview_prep():
    return render_template('interview/prep.html')

@interview_bp.route('/practice')
@login_required
def practice():
    return render_template('interview/practice.html') 