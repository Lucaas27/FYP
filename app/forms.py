from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, IntegerField, SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError, NumberRange
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
    picture = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])
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


class AddItemForm(FlaskForm):

    title = StringField('Title', validators=[
        DataRequired(), Length(min=4, max=140)])

    description = TextAreaField('Description', validators=[
        DataRequired(), Length(min=4, max=140)])

    quantity = IntegerField(
        "Quantity", validators=[DataRequired(message="Please only insert numerical values"), NumberRange(min=1)])

    item_location = StringField("Location", validators=[
        DataRequired(), Length(min=2, max=140)])

    condition = SelectField("Condition", validators=[DataRequired()], choices=[('Used', 'Used'),
                                                                               ('Like new',
                                                                                'Like new'),
                                                                               ('For parts or not working', 'For parts or not working')], default="Used")

    price = FloatField("Price", validators=[
        DataRequired("Please set a valid price")])

    pic_file = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])

    category = SelectField("Category", validators=[DataRequired(message="Please select a category")], choices=[('DSLR cameras', 'DSLR cameras'),
                                                                                                               ('Video camera',
                                                                                                                'Video cameras'),
                                                                                                               ('Flashguns',
                                                                                                                'Flashguns'),
                                                                                                               ('Studio equipment', 'Studio equipment'),
                                                                                                               ('Lenses', 'Lenses')], default="DSLR cameras")

    submit = SubmitField('Post')
