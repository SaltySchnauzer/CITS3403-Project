from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField, TextAreaField, DecimalRangeField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms.validators import DataRequired
from wtforms import fields



# -- Forms --


class SessionSummaryForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired()])
    productivity = DecimalRangeField("Productivity", validators=[DataRequired()])
    mood = RadioField("Mood", choices=[("sad", "😞"), ("neutral", "😐"), ("happy", "😊")], validators=[DataRequired()])
    description = TextAreaField("Description")
    task_type = SelectField("Type", choices=["Assignment", "Study", "Exam Prep", "Quiz"], validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')
        

class FriendSearchForm(FlaskForm):
    username = StringField('Search users', validators=[DataRequired()])
    submit = SubmitField('Add')