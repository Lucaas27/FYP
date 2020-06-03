from datetime import datetime, date
from app import db, login_manager, bcrypt
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm import column_property
import json
from sqlalchemy import TypeDecorator, String


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# many to many self referential relationship between users.follower_id and users.followed_id
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('users.id'))
                     )

# A user can have many addresses, an address can be for many users.
user_addresses = db.Table('user_addresses',
                          db.Column("user_id", db.Integer, db.ForeignKey(
                              "users.id")),
                          db.Column("address_id", db.Integer, db.ForeignKey("addresses.id")))

# An order can have many items, an item can be in many orders.
item_order = db.Table('item_order',
                      db.Column("order_id", db.Integer,
                                db.ForeignKey("orders.id")),
                      db.Column("item_for_sale_id", db.Integer, db.ForeignKey("for_sale.id")))


# Adds automatically updated created_at and updated_at timestamp columns to a table
class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# User can sell many items
# User can buy many items
# User can have many addresses
# User can follow many users
class User(db.Model, TimestampMixin, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(115), unique=True, nullable=False)
    image_file = db.Column(db.String(80), nullable=False,
                           default="default.jpg")
    password_hash = db.Column(db.String(60), nullable=False)
    # relationships (one to many)
    items_for_sale = db.relationship(
        "ItemForSale", backref="seller", lazy="dynamic")
    items_buyer = db.relationship("Order", backref="buyer", lazy="dynamic")
    # relationships (many to many)
    address = db.relationship(
        "Address", secondary="user_addresses", backref="user", lazy="dynamic"
    )
    followed = db.relationship(
        # User refers to the right side (followed) entity
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}')"

    def append_address(self, user_address):
        return self.address.append(user_address)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # check if a parent (left side) is already following the child (right side)
    # find all rows in the followers table where followed_id is user.id(follower)
    # it returns 0 for not following or 1 for following
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    # Join query to get recent items from the followed users ordered by date posted
    def followed_items(self):
        return ItemForSale.query.join(
            followers, (followers.c.followed_id == ItemForSale.seller_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    ItemForSale.id.desc())


# Type decorator will allow us to store a Json type column for item image_file field
class Json(TypeDecorator):

    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


# Item has one seller
# Item can be in many orders
# Item has one category
class ItemForSale(db.Model, TimestampMixin):
    __tablename__ = "for_sale"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    condition = db.Column(db.String(50), nullable=False)
    item_city = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    item_views = db.Column(db.Integer, default=0)
    image_file = db.Column(Json(128), nullable=False,
                           default=['item.jpg'])
    sold = db.Column(db.Boolean, default=False)

    # relationships
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    def __repr__(self):
        return f"ItemForSale('{self.title}', 'Quantity:{self.quantity}','{self.condition}', 'Cat:{self.category}')"


# The same address can belong to many users, a user can have many addresses.
# The same address can be in many orders, an order can have one address.
class Address(db.Model, TimestampMixin):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    post_code = db.Column(db.String(100), nullable=False)

    # relationships
    order = db.relationship(
        "Order", backref="order_address", lazy="dynamic")

    def __repr__(self):
        return f"Address('{self.id}', '{self.address}','{self.country}', '{self.city}', '{self.post_code}')"


# An order is for a buyer, a buyer can place many orders
# An order can have many items, an item can be in many orders
# An order has one address, an address can have many orders
class Order(db.Model, TimestampMixin):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    # relationships
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    item = db.relationship(
        "ItemForSale", secondary="item_order", backref="order", lazy="dynamic")
    order_address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))

    def __repr__(self):
        return f"Order('{self.item}', 'buyer_id: {self.buyer_id}')"


# Category has many items
class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    item_cat = db.relationship(
        "ItemForSale", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"Category('{self.name}')"


# Table needed for google OAuth
class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)
