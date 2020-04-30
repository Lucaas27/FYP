from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError
from app.models import User
from flask_wtf.file import FileAllowed
from flask_login import current_user


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name",
                            validators=[DataRequired(), Length(min=4, max=40)])
    username = StringField("Username", validators=[DataRequired(), Regexp(
        r'^[\w]+$', message="Please do not use special characters"), Length(min=4, max=15)])
    location = StringField("Location", validators=[
                           DataRequired(), Length(min=2, max=30)])
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


class UpdateDetailsForm(FlaskForm):
    full_name = StringField("Full name",
                            validators=[DataRequired(), Length(min=4, max=40)])
    username = StringField("Username", validators=[DataRequired(), Regexp(
        r'^[\w]+$', message="Please do not use special characters"), Length(min=4, max=15)])
    location = StringField("Location", validators=[
                           DataRequired(), Length(min=2, max=30)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    picture = FileField('image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
    # image_file = FileField()
    submit = SubmitField("Update")

    # Validate unique username
    def validate_username(self, username):
        if username.data != current_user.username:
            new_user = User.query.filter_by(username=username.data).first()
            if new_user is not None:
                raise ValidationError(
                    "Username alredy exists. Please chosse a different one.")

    # Validate unique email
    def validate_email(self, email):
        if email.data != current_user.email:
            new_user = User.query.filter_by(email=email.data).first()
            if new_user is not None:
                raise ValidationError(
                    "This email is linked to an existing account.")
