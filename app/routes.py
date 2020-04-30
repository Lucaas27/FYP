from flask import render_template, url_for, flash, redirect, request
import secrets
import os
from datetime import datetime, date
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateDetailsForm
from app.models import User, Item
from flask_login import login_user, current_user, logout_user, login_required


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        new_user = User(full_name=form.full_name.data.lower(), username=form.username.data.lower(), location=form.location.data.lower(),
                        email=form.email.data.lower(), password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Welcome {form.username.data}! You can now login!", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect(url_for("index"))
        else:
            flash(f"Please check your login details", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash(f"You are logged out", "info")

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html", title='About')


def save_pic(form_picture):
    random_hax = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hax + f_ext
    picture_path = os.path.join(
        app.root_path, "static", "img/profile/", picture_name)
    form_picture.save(picture_path)

    return picture_name


@app.route("/user/<user_id>/", methods=["GET", "POST"])
@login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()

    # Lets user update their details
    form = UpdateDetailsForm()
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.lower()
        current_user.username = form.username.data.lower()
        current_user.location = form.location.data.lower()
        current_user.email = form.email.data.lower()
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash("You have updated your information!", "success")
        return redirect(url_for("user", user_id=current_user.id))
    elif request.method == "GET":
        form.full_name.data = current_user.full_name
        form.username.data = current_user.username
        form.location.data = current_user.location
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='img/profile/' + user.image_file)

    user_items_count = Item.query.filter_by(owner=user).count()
    user_items_active = Item.query.filter_by(owner=user, sold=False).all()
    user_items_sold = Item.query.filter_by(owner=user, sold=True).all()

    return render_template("user.html", title='Account', image_file=image_file, form=form, user=user, user_items_active=user_items_active,
                           user_items_sold=user_items_sold, user_items_count=user_items_count)
