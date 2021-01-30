from flask import render_template, url_for, flash, redirect, request, jsonify, make_response, session, current_app
from sqlalchemy import desc, update, or_
import os
import secrets
import string
import stripe
from datetime import datetime, date
from app import app, db, bcrypt, mail
from app.forms import *
from app.models import *
from app.funcs import save_pic, send_reset_email, array_merge
from flask_login import login_user, current_user, logout_user, login_required
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import func
from flask_mail import Message


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.updated_at = datetime.utcnow()
        db.session.commit()


@app.context_processor
def inject_categories():
    # Display only categories with available items
    categories = Category.query.join(
        ItemForSale, (Category.id == ItemForSale.category_id)).filter(ItemForSale.sold == False).all()
    return dict(categories=categories)


@app.route("/")
@app.route("/index")
def index():
    page = request.args.get('page', 1, type=int)
    all_items = ItemForSale.query.filter_by(sold=False)\
        .order_by(ItemForSale.id.desc()).paginate(page, app.config['LISTINGS_PER_PAGE'], False)
    next_url = url_for('index', page=all_items.next_num) \
        if all_items.has_next else None
    prev_url = url_for('index', page=all_items.prev_num) \
        if all_items.has_prev else None
    return render_template("index.html", all_items=all_items.items, next_url=next_url,
                           prev_url=prev_url, page_num=all_items.iter_pages(), page=page)


@app.route('/search/cat/<cat_id>', methods=['GET', 'POST'])
@app.route('/search', methods=['GET', 'POST'])
def search(cat_id=None):
    page = request.args.get('page', 1, type=int)
    available_items = ItemForSale.query.filter_by(sold=False)\
        .order_by(ItemForSale.id.desc()).paginate(page, app.config['LISTINGS_PER_PAGE'], False)
    if cat_id is None:
        target_string = request.form['search']

        # Show all items that are available and match the search
        listings = ItemForSale.query.filter(
            or_(
                ItemForSale.title.contains(target_string),
                ItemForSale.description.contains(target_string)
            )
        ).filter(ItemForSale.sold == False).all()

        if target_string == '':
            search_msg = 'No record(s) found - displaying all records'
            color = 'danger'
        else:
            search_msg = f'{len(listings)} item(s) found'
            color = 'success'

    else:
        # inner join query returns all data from items that match the value of cat_id
        available_items = ItemForSale.query.join(
            Category, (ItemForSale.category_id == cat_id)).filter(ItemForSale.sold == False)\
            .paginate(page, app.config['LISTINGS_PER_PAGE'], False)
        next_url = url_for('search', cat_id=cat_id, page=available_items.next_num) \
            if available_items.has_next else None
        prev_url = url_for('search', cat_id=cat_id, page=available_items.prev_num) \
            if available_items.has_prev else None
        return render_template("search.html", available_items=available_items.items,
                               next_url=next_url, prev_url=prev_url, page=page, page_num=available_items.iter_pages())

    return render_template("_search.html", title='Search result', listings=listings,
                           search_msg=search_msg, color=color)


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
    if google.authorized:
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={
                "token": current_app.blueprints["google"].token["access_token"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if resp.ok:
            del current_app.blueprints["google"].token
            session.clear()
            logout_user()
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


@app.route("/contact", methods=["POST", "GET"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message('Customer Enquiry',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[app.config['MAIL_USERNAME']]
                      )
        msg.body = f'''
        From: {form.name.data}
        Email: {form.email.data}
        Message: {form.message.data}
        '''
        mail.send(msg)

        flash("Thank you for your message. We will get back to you shortly!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", title='Contact', form=form)


@app.route("/profile/<username>", methods=["GET"])
@login_required
def user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    rate = db.session.query(func.avg(Review.rating).label(
        'average')).filter(Review.user_reviewed_id == user.id)
    if rate[0].average:
        avg = round(rate[0].average, 2)
    else:
        avg = 0
    # Items from people the user follows
    items_following = current_user.followed_items().paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url_following = url_for('user', username=username, page=items_following.next_num) \
        if items_following.has_next else None
    prev_url_following = url_for('user', username=username, page=items_following.prev_num) \
        if items_following.has_prev else None

    # Number of items the user is selling
    user_items_count = ItemForSale.query.filter_by(seller=user).count()
    # Items sold
    user_items_sold = ItemForSale.query.filter_by(
        sold=True, seller=current_user).order_by(ItemForSale.id.desc()).paginate(
        page, app.config['LISTINGS_PER_PAGE'], False)
    next_url_sold = url_for('user', username=username, page=user_items_sold.next_num) \
        if items_following.has_next else None
    prev_url_sold = url_for('user', username=username, page=user_items_sold.prev_num) \
        if items_following.has_prev else None
    # Active items
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
                           next_url_sold=next_url_sold, prev_url_sold=prev_url_sold, average=avg)


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
                country=form.country.data.lower(),
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


@ app.route("/new_item/", methods=["GET", "POST"])
@ login_required
def new_item():
    form = AddItemForm()
    # List comprehension to fill category choices dinamically.
    form.category_id.choices = [(cat.id, cat.name)
                                for cat in Category.query.all()]
    ''' transforms user inputs using .lower to save into
            the database in a consistent way'''

    # if form.validate_on_submit():
    if form.picture.data:
        pics = save_pic(form.picture.data, "static/img/items")
        # Save picture to img/item path after resizing it
        # pics = []
        # if not form.picture.data or not any(item for item in form.picture.data):
        #     pics.append('item.jpg')
        # else:
        #     for item in form.picture.data:
        #         pic_item = save_pic(item, "static/img/items")
        #         pics.append(pic_item)

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
    return render_template("new_item.html",  form=form, title="New item")


@app.route("/item/<item_id>", methods=["GET", "POST"])
@ login_required
def item(item_id):
    form = AddToCartForm()
    # This is the item being viewed on the page.
    item = ItemForSale.query.filter_by(id=item_id).first_or_404()
    item.item_views += 1
    db.session.commit()

    if item in current_user.items_for_sale:

        # Delete listing
        if request.args.get('delete'):
            db.session.delete(item)
            db.session.commit()
            flash("You have deleted a listing!", "success")
            return redirect(url_for("index"))

    if form.validate_on_submit():
        quantity = form.quantity.data
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        elif quantity > item.quantity:
            flash(
                f'There are not enough units, please check availability.', 'danger')
            return redirect(url_for('item', item_id=item_id))
        else:

            item_array = {item_id: {'title': item.title, 'quantity': quantity, 'price': item.price, 'qt_available': item.quantity,
                                    'image': item.image_file[0], 'condition': item.condition, 'item_city': item.item_city}}
            session.modified = True
            # Checks to see if the user has already started a cart.
            if 'cart' in session:
                # If the item is already in the cart, update the quantity
                if item_id in session['cart']:
                    for key, value in session['cart'].items():
                        if item_id == key:
                            old_quantity = session['cart'][key]['quantity']
                            new_quantity = (int(old_quantity) + int(quantity))
                            session['cart'][key]['quantity'] = new_quantity
                            if new_quantity > item.quantity:
                                session['cart'][key]['quantity'] = item.quantity
                                flash(
                                    'You alredy have all items available in your cart', 'danger')
                                return redirect(url_for('item', item_id=item_id))

                # If the product is not in the cart, then add it.
                else:
                    session['cart'] = array_merge(
                        session['cart'], item_array
                    )

            else:
                # if the user has not started a cart, we start it and add the product.
                session['cart'] = item_array

    return render_template("item_details.html", title="Item Details", item=item, form=form)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    if 'cart' not in session:
        return render_template('cart.html', title='Cart')
    else:
        individual_quantity = 0
        price = 0
        subtotal = 0
        total = 0
        for key, value in session['cart'].items():
            individual_quantity = int(
                session['cart'][key]['quantity'])
            price = float(
                session['cart'][key]['price'])
            subtotal = (individual_quantity * price)
            # Add subtotal to cart session
            session['cart'][key]['subtotal'] = subtotal
            # Total value
            total += subtotal
            session['total'] = total

    if request.args.get('empty'):
        session.pop('cart', None)

    return render_template('cart.html', title='Cart', total=total)


@app.route("/delete_cart", methods=["POST", "GET"])
@login_required
def delete_cart():
    req = request.get_json()
    item_id = req['item_id']
    total = 0
    session['cart'].pop(item_id, None)
    for key, value in session['cart'].items():
        # calculate subtotal (quantity value stored * price)
        session['cart'][key]['subtotal'] = (
            float(session['cart'][key]['quantity']) *
            float(session['cart'][key]['price'])
        )
        # store value in a variable
        subtotal = session['cart'][key]['subtotal']
        # Total value
        total += float(subtotal)
        session['total'] = total

    session.modified = True
    return jsonify({'total': total})


@app.route("/update_cart", methods=["POST", "GET"])
@login_required
def update_cart():
    req = request.get_json()
    new_quantity = req['quantity']
    item_id = req['item_id']
    item = ItemForSale.query.get(item_id)
    qt_available = item.quantity
    total = 0

    # if the new quantity is higher than the quantity available
    if int(new_quantity) > qt_available:
        new_quantity = qt_available

    for key, value in session['cart'].items():
        if key == item_id:
            # it stores quantity value in the session
            session['cart'][item_id]['quantity'] = new_quantity
            # get the price
            price = float(session['cart'][item_id]['price'])
            # calculate subtotal (quantity value stored * price)
            session['cart'][item_id]['subtotal'] = (
                int(session['cart'][item_id]['quantity']) * price)
            # store value in a variable
            subtotal = session['cart'][item_id]['subtotal']
            total += float(subtotal)
            session['total'] = total

        else:
            # Total value (add all subtotals and store it in the total variable)
            individual_quantity = float(
                session['cart'][key]['quantity'])
            price = float(
                session['cart'][key]['price'])
            subtotal = float(individual_quantity * price)
            # Add subtotal to cart session
            session['cart'][key]['subtotal'] = subtotal

            # Total value
            total += float(subtotal)
            session['total'] = total

    session.modified = True
    return jsonify({'new_quantity': new_quantity, 'new_subtotal': subtotal, 'new_total': total,
                    'qt_available': qt_available})


@app.route("/new_order", methods=["GET", "POST"])
@login_required
def new_order():
    if 'cart' not in session:
        return redirect(url_for('login'))
    form = NewOrderForm()
    form.order_address_id.choices = [(add.id, '{}, {}, {}, {}'.format(add.address.title(), add.city.title(), add.country.upper(), add.post_code.title()))
                                     for add in current_user.address.all()]

    if request.args.get('new_address'):
        form = AddressForm()
        if form.validate_on_submit():
            new_address = Address(
                address=form.address.data.lower(),
                post_code=form.post_code.data.lower(),
                city=form.city.data.lower(),
                country=form.country.data.lower(),
            )

            db.session.add(new_address)
            current_user.append_address(new_address)
            db.session.commit()
            flash("You have added a new address!", "success")
            return redirect(url_for("new_order"))
        return render_template('address.html', form=form)

    if form.validate_on_submit():
        invoice = secrets.token_hex(5)
        total = 0
        order = Order(invoice=invoice, buyer=current_user,
                      order_address_id=form.order_address_id.data,
                      phone_number=form.phone_number.data)

        # Get item id and save it to the item_order table where
        # we can see all items for a certain order
        for key, value in session['cart'].items():
            item = ItemForSale.query.get(key)
            title = item.title
            item_pic = session['cart'][key]['image']
            quantity = int(session['cart'][key]['quantity'])
            price = float(
                session['cart'][key]['price'])
            subtotal = float(quantity * price)
            # Add subtotal to cart session
            session['cart'][key]['subtotal'] = subtotal
            # Total value
            total += float(subtotal)
            session['total'] = total

            qt_available = item.quantity
            order.total = total
            order_item = OrderItem(
                quantity=quantity, item=item, order=order, title=title, pic=item_pic)
            # It uptades the quantity available
            item.quantity = (qt_available - quantity)
            # Change item to sold if quantity is zero
            if item.quantity == 0:
                item.sold = True
            if item.quantity < 0:
                flash(
                    'You have items in your cart that are not available in that quantity', 'danger')
                return redirect(url_for('cart'))

            session.modified = True
            db.session.add(order_item)
            db.session.commit()

        # Process payment using stripe
        stripe.api_key = app.config['STRIPE_SECRET_KEY']
        amount = request.form.get('amount')
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken'],
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            description='Lensify',
            amount=int(session['total']*100),
            currency='gbp',
        )
        session.pop('cart', None)
        flash('Your order has been submitted.', 'success')
        return redirect(url_for('user_orders'))

    return render_template('new_order.html', form=form, total=session['total']*100)


@app.route("/user_orders", methods=["GET"])
@login_required
def user_orders():
    page = request.args.get('page', 1, type=int)
    user_id = current_user.id

    # all orders made by the user
    user_orders = Order.query.filter_by(buyer_id=user_id).order_by(Order.id.desc())\
        .paginate(page, app.config['LISTINGS_PER_PAGE'], False)
    order_item = OrderItem.query.join(
        Order, (OrderItem.order_id == Order.id)).all()

    next_url = url_for('user_orders', page=user_orders.next_num) \
        if user_orders.has_next else None
    prev_url = url_for('user_orders', page=user_orders.prev_num) \
        if user_orders.has_prev else None

    return render_template('user_orders.html', user_orders=user_orders.items, page=page,
                           next_url=next_url, prev_url=prev_url, page_num=user_orders.iter_pages())

# --------------------- Google OAuth login---------------------------------------------


@app.route("/google")
def gg_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    resp_json = resp.json()
    return redirect(url_for("index"))


# google blueprint
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
        flash("Failed to log in.", "error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, "error")
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
        flash("Successfully signed in.", "success")

    else:
        #  Create a random username and password for the new user
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        random_numb = secrets.randbelow(100000)
        username = info["given_name"] + info["family_name"]+str(random_numb)
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
        flash("Successfully signed in.", "success")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, "error")

# !-------------------------------- Google OAuth 2.0 login end -------------------------------------!
