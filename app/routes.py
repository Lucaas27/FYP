from flask import render_template, url_for, flash, redirect
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Listing, Bid


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
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
    form = LoginForm()
    if form.validate_on_submit():
        flash(f"Welcome back {form.username.data}!", "success")
        return redirect(url_for("login"))
    return render_template("login.html", title="Login", form=form)


@app.route("/about")
def about():
    return render_template("about.html", title='About')
