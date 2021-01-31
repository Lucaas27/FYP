from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, MultipleFileField, IntegerField, SelectField, FloatField, TextAreaField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from wtforms_validators import AlphaNumeric, Alpha, Integer
from app.models import User
from flask_wtf.file import FileAllowed
from flask_login import current_user
from country_list import countries_for_language
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
import phonenumbers

# Countries list
choice = countries_for_language('en')


class RegistrationForm(FlaskForm):
    first_name = StringField("First name",
                             validators=[DataRequired(), Alpha(
                                 message="Please use alphabetic characters only"),
                                 Length(min=3, max=20)])

    last_name = StringField("Last name",
                            validators=[DataRequired(), Alpha(
                                message="Please use alphabetic characters only"),
                                Length(min=3, max=20)])

    username = StringField("Username", validators=[
                           DataRequired(),  AlphaNumeric(
                               message="Please use alphabetic characters and numbers only"),
                           Length(min=4, max=12)])

    email = StringField("Email",
                        validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[
                             DataRequired(), Length(min=4, max=25)])

    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password", message='Passwords must match'), Length(min=4, max=25)])
    submit = SubmitField("Sign Up")

    # Validate unique username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError(
                "Username alredy exists. Please chosse a different one."
            )

    # Validate unique email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError(
                "This email is linked to an existing account.")


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=4, max=15)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ResetForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Email me")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is None:
            raise ValidationError(
                "This email is not linked to an existing account."
            )


class NewPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=4, max=25)])

    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password", message='Passwords must match'), Length(min=4, max=25)])
    submit = SubmitField("Reset password")


class UpdateDetailsForm(FlaskForm):

    first_name = StringField("First name",
                             validators=[DataRequired(), Alpha(
                                 message="Please use alphabetic characters only"),
                                 Length(min=3, max=20)])

    last_name = StringField("Last name",
                            validators=[DataRequired(), Alpha(
                                message="Please use alphabetic characters only"),
                                Length(min=3, max=20)])

    username = StringField("Username", validators=[
                           DataRequired(),  AlphaNumeric(
                               message="Please use alphabetic characters and numbers only"),
                           Length(min=4, max=12)])

    email = StringField("Email",
                        validators=[DataRequired(), Email()])

    picture = FileField('Profile picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])

    submit_details = SubmitField("Update")

    # Validate unique username
    def validate_username(self, username):
        if username.data.lower() != current_user.username:
            user = User.query.filter_by(username=username.data.lower()).first()
            if user is not None:
                raise ValidationError(
                    "Username alredy exists. Please chosse a different one.")

    # Validate unique email
    def validate_email(self, email):
        if email.data.lower() != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user is not None:
                raise ValidationError(
                    "This email is linked to an existing account.")


class AddressForm(FlaskForm):

    address = StringField("Street address", validators=[
                          DataRequired(), Length(min=5, max=30)])

    country = SelectField("Country", validators=[
                          DataRequired()], choices=choice)

    city = StringField("City", validators=[
                       DataRequired(), Length(min=5, max=30)])

    post_code = StringField("Post Code", validators=[
                            DataRequired(), Length(min=5, max=30)])

    submit_address = SubmitField("Submit")


class AddItemForm(FlaskForm):

    title = StringField('Title', validators=[
        DataRequired(), Length(min=4, max=140)])

    description = TextAreaField('Description', validators=[
        DataRequired(), Length(min=4, max=500)])

    quantity = h5fields.IntegerField(
        "Quantity", default=1, widget=h5widgets.NumberInput(min=1, max=100, step=1), validators=[DataRequired(message="Please only insert numerical values")])

    item_city = StringField("City", validators=[
        DataRequired(), Length(min=3, max=140)])

    condition = SelectField("Condition", validators=[DataRequired()], choices=[('Used', 'Used'),
                                                                               ('Like new',
                                                                                'Like new'),
                                                                               ('For parts or not working', 'For parts or not working')], default="Used")

    price = h5fields.DecimalField("Price", default=0, widget=h5widgets.NumberInput(min=0, step="0.01"), validators=[
        DataRequired("Please set a valid price")])

    picture = MultipleFileField('Images (Up to 4)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'])])

    category_id = SelectField('Select category', coerce=int)

    submit = SubmitField('Post')


class AddToCartForm(FlaskForm):

    quantity = h5fields.IntegerField(
        "Quantity", default=1, widget=h5widgets.NumberInput(min=1, max=100, step=1),
        validators=[DataRequired(message="Please only insert numerical values")])

    submit = SubmitField('Add to cart')


class NewOrderForm(FlaskForm):
    order_address_id = SelectField('Shipping address', coerce=int, validators=[
                                   DataRequired(message="Please insert an address")])
    phone_number = StringField('Phone Number', validators=[
        DataRequired(), Length(min=5, max=30), Regexp(
            r'^[0-9]+$', message="Please only use numbers")])

    submit = SubmitField('Pay Now')


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[
                       DataRequired(), Length(min=3, max=50)])

    email = h5fields.EmailField(
        'Email', validators=[DataRequired(message="Please insert an email")])
    message = TextAreaField('Message', validators=[
                            DataRequired(message="Please insert a message")])
    submit = SubmitField('Contact')
