from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, ValidationError
from wtforms.validators import DataRequired

class InterviewQuestionsForm(FlaskForm):
    prompt = TextAreaField('Resume/Job Description', validators=[
        DataRequired(message='Please provide your resume or job description')
    ], render_kw={
        'placeholder': 'Paste your resume, job description, or list your skills',
        'minlength': 1,
        'rows': 6
    })
    submit = SubmitField('Generate Interview Questions')



class InterviewAnswersForm(FlaskForm):
    answers = TextAreaField('Answers', validators=[
        DataRequired(message='Please provide your answers to the questions')
    ], render_kw={
        'rows': 3,
        'placeholder': 'Type your answers here...'
    })
    submit = SubmitField('Submit Answers')
