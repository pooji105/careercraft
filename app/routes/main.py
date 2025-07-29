from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Always render the home page at root
    return render_template('main/home.html')

@main_bp.route('/home')
def home():
    # Explicit home route that renders the home page
    return render_template('main/home.html')

@main_bp.route('/resources')
def resources():
    return render_template('resources.html')