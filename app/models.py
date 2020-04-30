from datetime import datetime, date
from app import db, login_manager
from flask_login import UserMixin

# A user can have many items (many to one | users - items)
# An item has one seller (One to many | items - users)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    # relationships
    items = db.relationship("Item", backref="owner", lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


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
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    category = db.Column(db.String(50), unique=False, nullable=False)
    sold = db.Column(db.Boolean, default=False)
    # relationships
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"Item('{self.title}', '{self.quantity}','{self.condition}', '{self.category}', '{self.description}', '{self.sold}')"
