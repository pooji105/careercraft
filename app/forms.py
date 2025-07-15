from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    current_role = SelectField('Current Role (Optional)', choices=[
        ('', 'Select your current role'),
        ('student', 'Student'),
        ('entry_level', 'Entry Level'),
        ('mid_level', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('manager', 'Manager'),
        ('executive', 'Executive'),
        ('freelancer', 'Freelancer'),
        ('unemployed', 'Unemployed'),
        ('other', 'Other')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Login')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired(), Length(min=1, max=100)])
    category = StringField('Category', validators=[Length(max=100)])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    submit = SubmitField('Save Skill') 