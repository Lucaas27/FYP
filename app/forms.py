from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name",
                            validators=[DataRequired(), Length(min=6, max=40)])
    username = StringField("Username",
                           validators=[DataRequired(), Regexp(r'^[\w]+$', message="Please do not use special characters"), Length(min=4, max=15)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Regexp(r'^[\w]+$', message="Please do not use special characters"), Length(min=4, max=25)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password", message='Passwords must match'), Length(min=4, max=15)])
    submit = SubmitField("Sign Up")

    # Validate unique username
    def validate_username(self, username):
        new_user = User.query.filter_by(username=username.data).first()
        if new_user is not None:
            raise ValidationError(
                "Username alredy exists. Please chosse a different one.")

    # Validate unique email
    def validate_email(self, email):
        new_user = User.query.filter_by(email=email.data).first()
        if new_user is not None:
            raise ValidationError(
                "This email is linked to an existing account.")


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=4, max=15)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
