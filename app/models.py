from app.extensions import db
from app import login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)  # Increased from 100 to 150
    email = db.Column(db.String(150), unique=True, nullable=False)  # Increased from 120 to 150
    password_hash = db.Column(db.String(512), nullable=False)  # Increased to 512 to be safe
    current_role = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resumes = db.relationship('Resume', backref='user', lazy=True)
    resume_analyzers = db.relationship('ResumeAnalyzer', backref='user', lazy=True)
    job_applications = db.relationship('JobApplication', backref='user', lazy=True)
    skills = db.relationship('Skill', backref='user', lazy=True)
    interview_feedbacks = db.relationship('InterviewFeedback', backref='user', lazy=True)
    job_matches = db.relationship('JobMatch', backref='user', lazy=True)
    job_match_histories = db.relationship('JobMatchHistory', backref='user', lazy=True)
    
    # Resume builder relationships
    personal_info = db.relationship('UserPersonalInfo', backref='user', lazy=True, uselist=False)
    education = db.relationship('UserEducation', backref='user', lazy=True, cascade='all, delete-orphan')
    experience = db.relationship('UserExperience', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('UserProjects', backref='user', lazy=True, cascade='all, delete-orphan')
    resume_skills = db.relationship('UserSkills', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.email}>'

class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Text, nullable=True)  # Added the 'data' field
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Resume {self.id}>'

class UserPersonalInfo(db.Model):
    __tablename__ = 'user_personal_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    summary = db.Column(db.Text)
    linkedin_display = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(255))
    github_display = db.Column(db.String(100))
    github_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserPersonalInfo {self.full_name}>'

class UserEducation(db.Model):
    __tablename__ = 'user_education'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(150), nullable=False)
    year = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserEducation {self.institution} - {self.degree}>'

class UserExperience(db.Model):
    __tablename__ = 'user_experience'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserExperience {self.title} at {self.company}>'

class UserProjects(db.Model):
    __tablename__ = 'user_projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProjects {self.title}>'

class UserSkills(db.Model):
    __tablename__ = 'user_skills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='General')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserSkills {self.name} ({self.category})>'

class ResumeAnalyzer(db.Model):
    __tablename__ = 'resume_analyzer'
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
    category = db.Column(db.String(50))
    rating = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # The relationship is already defined in the User model

class InterviewFeedback(db.Model):
    __tablename__ = 'interview_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Resume information
    resume_filename = db.Column(db.String(255), nullable=True)  # Uploaded resume file name or path
    
    # JSON storage for complete data with server defaults
    questions_json = db.Column(db.Text, nullable=False, server_default='[]')  # Store questions as JSON array
    answers_json = db.Column(db.Text, nullable=False, server_default='[]')    # Store answers as JSON array
    model_answers_json = db.Column(db.Text, nullable=False, server_default='[]')  # Store ideal/model answers as JSON array
    feedback_json = db.Column(db.Text, nullable=False, server_default='[]')   # Store AI feedback as JSON array
    
    # Individual fields for quick access (optional)
    question = db.Column(db.Text, nullable=True)  # First question for quick reference
    answer = db.Column(db.Text, nullable=True)    # First answer for quick reference
    model_answer = db.Column(db.Text, nullable=True)  # First model answer for quick reference
    feedback = db.Column(db.Text, nullable=True)  # First feedback for quick reference
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_filename': self.resume_filename,
            'questions_json': self.questions_json,
            'answers_json': self.answers_json,
            'model_answers_json': self.model_answers_json,
            'feedback_json': self.feedback_json,
            'question': self.question,
            'answer': self.answer,
            'model_answer': self.model_answer,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<InterviewFeedback {self.id} - {self.question[:50] if self.question else "No question"}>'


class InterviewResponse(db.Model):
    __tablename__ = 'interview_response'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_filename = db.Column(db.String(255), nullable=True)  # Uploaded resume file name or path
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(50), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    model_answer = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='interview_responses')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_filename': self.resume_filename,
            'question': self.question,
            'answer': self.answer,
            'verdict': self.verdict,
            'feedback': self.feedback,
            'model_answer': self.model_answer,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<InterviewResponse {self.id} - {self.verdict}>'

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