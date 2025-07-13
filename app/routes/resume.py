from flask import Blueprint, render_template
from flask_login import login_required

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/')
@login_required
def resume_builder():
    return render_template('resume/builder.html')

@resume_bp.route('/templates')
@login_required
def templates():
    return render_template('resume/templates.html') 