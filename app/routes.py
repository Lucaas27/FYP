from flask import render_template, url_for, flash, redirect, request, jsonify
from sqlalchemy import desc, update
import os
import secrets
import string
from datetime import datetime, date
from app import app, db, bcrypt
from app.forms import *
from app.models import *
from app.funcs import save_pic, send_reset_email
from flask_login import login_user, current_user, logout_user, login_required
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.updated_at = datetime.utcnow()
        db.session.commit()


@app.context_processor
def inject_categories():
    # Display only categories with available items
    categories = Category.query.join(
        ItemForSale, (Category.id == ItemForSale.category_id)).all()
    return dict(categories=categories)


@app.route("/")
@app.route("/index")
def index():
    page = request.args.get('page', 1, type=int)
    all_items = ItemForSale.query.order_by(ItemForSale.id.desc()).paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url = url_for('index', page=all_items.next_num) \
        if all_items.has_next else None
    prev_url = url_for('index', page=all_items.prev_num) \
        if all_items.has_prev else None
    return render_template("index.html", all_items=all_items.items, next_url=next_url,
                           prev_url=prev_url, page_num=all_items.iter_pages(), page=page)


@app.route('/search/<cat_id>', methods=['GET', 'POST'])
def search(cat_id=None):
    page = request.args.get('page', 1, type=int)
    available_items = ItemForSale.query.paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    if cat_id is not None:
        # inner join query returns all data from items that match the value of cat_id
        available_items = ItemForSale.query.join(
            Category, (ItemForSale.category_id == cat_id)).paginate(
            page, app.config['LISTINGS_PER_PAGE'], False)
        next_url = url_for('search', page=available_items.next_num) \
            if available_items.has_next else None
        prev_url = url_for('search', page=available_items.prev_num) \
            if available_items.has_prev else None
        return render_template("search.html", available_items=available_items.items,
                               next_url=next_url, prev_url=prev_url, page=page, page_num=available_items.iter_pages())
    return render_template("search.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(first_name=form.first_name.data.lower(),
                    last_name=form.last_name.data.lower(),
                    username=form.username.data.lower(),
                    email=form.email.data.lower(),
                    password_hash=bcrypt.generate_password_hash(
                    form.password.data).decode("utf-8")
                    )

        db.session.add(user)
        db.session.commit()
        flash(f"Welcome {user.username}! You can now login!", "success")
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
            flash("Please check your login details", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash(f"You have logged out", "info")
    return redirect(url_for("index"))


@app.route("/reset_password", methods=["POST", "GET"])
def request_new_password():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        send_reset_email(user)
        flash(f"Please check your email and follow the instructions to reset your password.", "info")
        return redirect(url_for('login'))
    return render_template("request_new_password.html", title="Password Reset", form=form)


@app.route("/reset_password/<token>", methods=["POST", "GET"])
def request_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_token(token)
    if user is None:
        flash(f"This token is invalid or expired.", "danger")
        return redirect(url_for("request_new_password"))
    form = NewPasswordForm()
    if form.validate_on_submit():
        password_hashed = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user.password_hash = password_hashed
        db.session.commit()
        flash(f"You have successfully changed your password!", "success")
        return redirect(url_for("login"))
    return render_template("set_new_password.html", title="Password Reset", form=form)


@app.route("/about")
def about():
    return render_template("about.html", title='About')


@app.route("/profile/<username>", methods=["GET"])
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    categories = Category.query.join(
        ItemForSale, (Category.id == ItemForSale.category_id)).all()

    items_following = current_user.followed_items().paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url_following = url_for('user', username=username, page=items_following.next_num) \
        if items_following.has_next else None
    prev_url_following = url_for('user', username=username, page=items_following.prev_num) \
        if items_following.has_prev else None

    user_items_count = ItemForSale.query.filter_by(seller=user).count()

    user_items_sold = ItemForSale.query.filter_by(
        sold=True, seller=current_user).order_by(ItemForSale.id.desc()).paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url_sold = url_for('user', username=username, page=user_items_sold.next_num) \
        if items_following.has_next else None
    prev_url_sold = url_for('user', username=username, page=user_items_sold.prev_num) \
        if items_following.has_prev else None

    user_items_active = ItemForSale.query.filter_by(
        seller=user, sold=False).order_by(ItemForSale.id.desc()).paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url_active = url_for('user', username=username, page=user_items_active.next_num) \
        if items_following.has_next else None
    prev_url_active = url_for('user', username=username, page=user_items_active.prev_num) \
        if items_following.has_prev else None

    return render_template("user.html", title="Account", user=user, user_items_active=user_items_active.items,
                           user_items_count=user_items_count, user_items_sold=user_items_sold.items,
                           items_following=items_following.items, page_num=items_following.iter_pages(),
                           page_num1=user_items_sold.iter_pages(), page_num2=user_items_active.iter_pages(),
                           page=page, next_url_active=next_url_active, prev_url_active=prev_url_active,
                           next_url_following=next_url_following, prev_url_following=prev_url_following,
                           next_url_sold=next_url_sold, prev_url_sold=prev_url_sold)


# User info and addresses
@app.route("/profile/settings", methods=["POST", "GET"])
@app.route("/profile/settings/<address_id>", methods=["POST", "GET"])
@login_required
def user_settings(address_id=None):
    user = User.query.filter_by(id=current_user.id).first_or_404()
    form = UpdateDetailsForm(obj=user)
    all_user_addresses = user.address.all()

    # Submit forms separetely
    # Update user info
    if form.submit_details.data and form.validate_on_submit():
        form.populate_obj(user)
        if form.picture.data:
            picture_file = save_pic(form.picture.data, "static/img/profile")
            user.image_file = picture_file
        db.session.commit()
        flash("You have updated your information!", "success")
        return redirect(url_for("user_settings"))

    # Add new address
    if request.args.get('add_address'):
        form = AddressForm()

        if form.submit_address.data and form.validate_on_submit():
            new_address = Address(
                address=form.address.data.lower(),
                post_code=form.post_code.data.lower(),
                city=form.city.data.lower(),
                country=form.country.data,
            )

            db.session.add(new_address)
            user.append_address(new_address)
            db.session.commit()
            flash("You have added a new address!", "success")
            return redirect(url_for("user_settings"))
        return render_template("address.html", form=form)

    # Update address
    if request.args.get('update') and address_id is not None:
        address = Address.query.get(address_id)
        if address in current_user.address:
            form = AddressForm(obj=address)
            # Update address
            if form.validate_on_submit():
                form.populate_obj(address)
                db.session.commit()
                flash("You have updated your address!", "success")
                return redirect(url_for("user_settings"))
        else:
            return render_template('404.html')
        return render_template("update_address.html", form=form)

    # Delete address
    if request.args.get('delete') and address_id is not None:
        address = Address.query.get(address_id)
        if address in current_user.address:
            db.session.delete(address)
            db.session.commit()
            flash("You have deleted an address!", "success")
            return redirect(url_for("user_settings"))
        else:
            return render_template('404.html')
        return render_template("update_address.html", form=form)

    return render_template("user_settings.html", title="User Settings", form=form,
                           all_user_addresses=all_user_addresses)


@ app.route('/follow/<username>')
@ login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {user.username} not found.', "danger")
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!', "info")
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {user.username}!', "success")
    return redirect(url_for('user', username=username))


@ app.route('/unfollow/<username>')
@ login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {user.username} not found.', "danger")
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', "info")
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You unfollowed {user.username}.', "info")
    return redirect(url_for('user', username=username))


@ app.route("/add_item/", methods=["GET", "POST"])
@ login_required
def add_item():
    form = AddItemForm()
    # List comprehension to fill category choices dinamically.
    form.category_id.choices = [(cat.id, cat.name)
                                for cat in Category.query.all()]
    ''' transform user inputs using .lower to save into
            the database in a consistent way'''

    if form.validate_on_submit():
        # Save picture to img/item path after resizing it
        if form.picture.data:
            pics = []
            for item in form.picture.data:
                pic_item = save_pic(item, "static/img/items")
                pics.append(pic_item)
        else:
            pic_item = 'item.jpg'

        new_item = ItemForSale(title=form.title.data.lower(),
                               description=form.description.data.lower(),
                               quantity=form.quantity.data,
                               item_city=form.item_city.data.lower(),
                               condition=form.condition.data,
                               price=form.price.data,
                               image_file=pics,
                               category_id=form.category_id.data,
                               seller_id=current_user.id
                               )

        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('item',
                                item_id=new_item.id))
    return render_template("add_item.html",  form=form, title="New item")


@ app.route("/item/<item_id>", methods=["GET", "POST"])
def item(item_id):
    item = ItemForSale.query.filter_by(id=item_id).first_or_404()
    return render_template("item_details.html", title="Item Details", item=item)


# --------------------- Google OAuth login---------------------------------------------


@app.route("/google")
def gg_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    resp_json = resp.json()
    return redirect(url_for("index"))


blueprint = make_google_blueprint(
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(
        OAuth, db.session, user=current_user, user_required=False),
)
app.register_blueprint(blueprint, url_prefix="/login")

# create/login local user on successful OAuth login


@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    info = resp.json()
    user_id = info["id"]

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(provider=blueprint.name,
                      provider_user_id=user_id, token=token)

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in.")

    else:
        #  Create a random username and password for the new user
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        x = secrets.randbelow(100)
        username = info["given_name"] + info["family_name"]+str(x)
        # Create a new local user account for this user
        user = User(
            username=username, first_name=info["given_name"], last_name=info["family_name"],
            email=info["email"], password_hash=bcrypt.generate_password_hash(
                password).decode("utf-8")
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")

# !-------------------------------- Google OAuth 2.0 login end -------------------------------------!
