from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import desc
import os
from app.funcs import save_pic
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
@app.route('/index/<cat_id>', methods=['GET', 'POST'])
def index(cat_id=None):
    
    # filter only available items
    available_items = Item.query.filter_by(sold=False).all()
    
    if cat_id is not None:
        #inner join query returns all data from items that match the value of cat_id
        available_items= Item.query.filter_by(sold=False).join(Category, (Item.category_id == cat_id)).all()

    # Display only categories with available items
    categories = Category.query.join(Item, (Category.id == Item.category_id)).filter_by(sold=False).all()
    
    return render_template("index.html", available_items=available_items, categories=categories)



@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        
        new_user = User(full_name=form.full_name.data.lower(), username=form.username.data.lower(), 
                        location=form.location.data.lower(), seller=form.seller.data,
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
        if user and user.check_password(form.password.data):
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
            picture_file = save_pic(form.picture.data, "static/img/profile")
            current_user.image_file = picture_file
        db.session.commit()
        flash("You have updated your information!", "success")
        return redirect(url_for("user", user_id=current_user.id))
    elif request.method == "GET":
        form.full_name.data = current_user.full_name
        form.username.data = current_user.username
        form.location.data = current_user.location
        form.email.data = current_user.email
    
    items_following = current_user.followed_items().all()
    user_items_count = Item.query.filter_by(owner=user).count()
    user_items_active = Item.query.filter_by(owner=user, sold=False).all()
    user_items_sold = Item.query.filter_by(owner=user, sold=True).all()

    return render_template("user.html", title='Account', form=form, user=user, user_items_active=user_items_active,
                           user_items_sold=user_items_sold, user_items_count=user_items_count,  items_following= items_following)

@app.route('/follow/<user_id>')
@login_required
def follow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f'User {user.username} not found.', "danger")
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!', "info")
        return redirect(url_for('user', user_id=current_user.id))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {user.username}!', "success")
    return redirect(url_for('user', user_id=user_id))

@app.route('/unfollow/<user_id>')
@login_required
def unfollow(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f'User {user.username} not found.', "danger")
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', "info")
        return redirect(url_for('user', user_id=current_user.id))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You unfollowed {user.username}.', "info")
    return redirect(url_for('user', user_id=user_id))

@app.route("/add_item/", methods=["GET", "POST"])
@login_required
def add_item():
    form = AddItemForm()
    # List comprehension
    form.category_id.choices = [(cat.id, cat.name)
                                for cat in Category.query.all()]
    ''' transform user inputs using .lower to save into
            the database in a consistent way'''

    if form.validate_on_submit():
        # Save picture to img item path after resizing it
        # save_file function cannot be used as it is a different path
        if form.pic_file.data:
            item_pic = save_pic(form.pic_file.data, "static/img/items")
        else:
            item_pic = 'item.jpg'

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
def item(item_id):
    item = Item.query.filter_by(id=item_id).first_or_404()
    image_file = url_for('static', filename='img/items/' + item.image_file)

    return render_template("item_details.html", title="Item Details", item=item, image_file=image_file)
