from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class SkillForm(FlaskForm):
    """Form for adding or editing a skill."""
    name = StringField('Skill Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message='Rating must be between 1 and 5')
    ])
    submit = SubmitField('Save')
