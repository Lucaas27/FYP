from datetime import datetime, time, date
from app import db

# A seller can have many listings and a listing has one seller (many to one | users - listings)
# A bidder can place many bids (one to many | users-bids)
# A listing can have many bids and a bid is for one listing (many to one | listing-bids)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    email = db.Column(db.String(115), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    # relationships
    seller = db.relationship("Listing", backref="seller", lazy=True)
    bidder = db.relationship("Bid", backref="bidder", lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False, default=1)
    location = db.Column(db.String(50), unique=False, nullable=False)
    condition = db.Column(db.String(50), unique=False, nullable=False)
    minimal_price = db.Column(db.Integer, unique=False, nullable=False)
    end_day = db.Column(db.Date, default=datetime.now, nullable=False)
    end_time = db.Column(db.Time, default=time, nullable=False)
    listing_views = db.Column(db.Integer, default=0)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default-listing.jpg')
    category = db.Column(db.String(50), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    available = db.Column(db.Boolean, default=True, nullable=False)

    # relationships
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    listing = db.relationship("Bid", backref="listing", lazy=True)

    def __repr__(self):
        return f"Listing('{self.title}', '{self.quantity}','{self.condition}', '{self.category}', '{self.description}', '{self.created_at}', '{self.available}')"


class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    bid_time = db.Column(db.DateTime, default=datetime.now)
    price = db.Column(db.Integer, nullable=False)

    # relationships
    bidder_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"))

    def __repr__(self):
        return f"Listing('Bidder_id:{self.bidder_id}', Bid_is_for_listing_id:'{self.listing_id}', 'Price:{self.price}', 'Bid_time:{self.bid_time}')"
