from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp


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


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Regexp(r'^[\w]+$', message="Please do not use special characters"), Length(min=4, max=15)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
