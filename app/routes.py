from flask import render_template, url_for, flash, redirect
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Listing, Bid
from flask_login import login_user, current_user, logout_user


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
        new_user = User(full_name=form.full_name.data, username=form.username.data,
                        email=form.email.data, password_hash=hashed_password)
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
            flash(f"You are logged in!", "success")
            return redirect(url_for("index"))
        else:
            flash(f"Please check your login details", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash(f"You are logged out", "danger")

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html", title='About')
