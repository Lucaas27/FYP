from datetime import datetime, date
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# User has many items
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    image_file = db.Column(db.String(80), nullable=False,
                           default="default.jpg")
    email = db.Column(db.String(115), unique=True, nullable=False)
    location = db.Column(db.String(50), unique=False, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.now)
    seller = db.Column(db.Boolean, default=False)

    # relationships
    items = db.relationship("Item", back_populates="owner", lazy="dynamic")

    def __repr__(self):
        return f"User('{self.username}')"


# Item has one owner
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False, default=1)
    item_location = db.Column(db.String(50), unique=False, nullable=False)
    condition = db.Column(db.String(50), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)
    item_views = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(80), nullable=False,
                           default='default-item.jpg')
    sold = db.Column(db.Boolean, default=False)
    terms = db.Column(db.Boolean, default=True)
    # relationships
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="items")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", back_populates="item_cat")

    def __repr__(self):
        return f"Item('{self.title}', '{self.quantity}','{self.condition}', '{self.category_id}', '{self.sold}')"


# Category has many items
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    item_cat = db.relationship("Item", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"Category('{self.name}')"
