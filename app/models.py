from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    current_role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resumes = db.relationship('Resume', backref='user', lazy=True)
    uploaded_resumes = db.relationship('UploadedResume', backref='user', lazy=True)
    job_applications = db.relationship('JobApplication', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    interview_feedbacks = db.relationship('InterviewFeedback', backref='user', lazy=True)
    job_matches = db.relationship('JobMatch', backref='user', lazy=True)
    job_match_histories = db.relationship('JobMatchHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_json = db.Column(db.Text, nullable=False)  # Store JSON as text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UploadedResume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    suggestions = db.Column(db.Text)  # Store suggestions as text/JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='applied')
    notes = db.Column(db.Text)
    jd_file = db.Column(db.String(255))  # Job description file name/path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    rating = db.Column(db.Integer)  # 1-5 or 1-10 scale

class InterviewFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions_json = db.Column(db.Text, nullable=False)  # Store JSON as text
    feedback_json = db.Column(db.Text, nullable=False)   # Store JSON as text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JobMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    skills = db.Column(db.Text)  # Store as comma-separated or JSON
    certifications = db.Column(db.Text)  # Store as comma-separated or JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JobMatch {self.job_title} for User {self.user_id}>'

class JobMatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    input_text = db.Column(db.Text, nullable=False)
    matched_roles_json = db.Column(db.Text, nullable=False)  # Store AI response as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<JobMatchHistory {self.id} for User {self.user_id}>' 