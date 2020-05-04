from datetime import datetime, date
from app import db, login_manager, bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# many to many self referential relationship between users.follower_id and users.followed_id
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

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
    items = db.relationship("Item", backref="owner", lazy="dynamic")
    followed = db.relationship(
        # User refers to the right side (followed) entity with follower_id backref
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}')"

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
    # it returns 0 for not following or 1 for follwoing 
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    
    # Join query to get recent items from the followed users ordered by date posted
    def followed_items(self):
        return Item.query.join(
            followers, (followers.c.followed_id == Item.owner_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Item.date_posted.desc())




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
                           default='item.jpg')
    sold = db.Column(db.Boolean, default=False)
    terms = db.Column(db.Boolean, default=True)
    # relationships
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    def __repr__(self):
        return f"Item('{self.title}', '{self.quantity}','{self.condition}', '{self.category_id}', '{self.sold}')"


# Category has many items
class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    item_cat = db.relationship("Item", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"Category('{self.name}')"

