from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import desc
import secrets
import os
from PIL import Image
from datetime import datetime, date
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateDetailsForm, AddItemForm
from app.models import User, Item, Category
from flask_login import login_user, current_user, logout_user, login_required


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/")
@app.route("/index")
def index():
    #filter only available items
    available_items = Item.query.filter_by(sold=False)
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        new_user = User(full_name=form.full_name.data.lower(), username=form.username.data.lower(), location=form.location.data.lower(), seller=form.seller.data,
                        email=form.email.data.lower(), password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Welcome {new_user.username}! You can now login!", "success")
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
    flash(f"You have logged out", "info")

    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html", title='About')

# compress and save picture with a random hex in the name
def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)

    picture_name = random_hex + f_ext

    picture_path = os.path.join(
        app.root_path, "static", "img/profile/", picture_name)

    output_size = (300, 300)
    im = Image.open(form_picture)
    i = im.convert("RGB")
    i.thumbnail(output_size)

    i.save(picture_path)

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


@app.route("/add_item/", methods=["GET", "POST"])
@login_required
def add_item():
    form = AddItemForm()
    form.category_id.choices = [(cat.id, cat.name.title())
                                for cat in Category.query.all()]
    ''' transform user inputs using .lower to save into
            the database in a consistent way'''

    if form.validate_on_submit():
        item_pic = 'default.jpg'
        # Save picture to img item path after resizing it
        # save_file function cannot be used as it is a different path
        if form.pic_file.data:

            pic = form.pic_file.data
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(pic.filename)
            picture_name = random_hex + f_ext
            picture_path = os.path.join(
                app.root_path, "static", "img/items/", picture_name)
            output_size = (300, 300)
            im = Image.open(pic)
            i = im.convert("RGB")
            i.thumbnail(output_size)
            i.save(picture_path)
            item_pic = picture_path

        new_item = Item(title=form.title.data.lower(),
                        description=form.description.data.lower(),
                        quantity=form.quantity.data,
                        item_location=form.item_location.data,
                        condition=form.condition.data,
                        price=form.price.data,
                        image_file=item_pic,
                        category_id=form.category_id.data,
                        owner_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('item',
                                item_id=new_item.id))
    return render_template("add_item.html",  form=form, title="New item")


@app.route("/item/<item_id>", methods=["GET", "POST"])
@login_required
def item(item_id):
    item = Item.query.filter_by(id=item_id).first_or_404()
    image_file = url_for(
        'static', filename='img/items/' + item.image_file)
    return render_template("itemDetails.html", title="Item Details", image_file=image_file, item=item)
