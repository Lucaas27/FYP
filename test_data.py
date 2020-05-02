from app import db, models, bcrypt
from app.models import User, Item, Category
from datetime import datetime


def add_user():
    
    u1 = User(
        full_name='Lucas Gomes',
        username='admin',
        email='admin@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
        location='UK',
        seller=True
    )
    
    u1 = User(
        full_name='user 1',
        username='user1',
        email='user1@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
        location='UK',
        seller=True
    )
    u2 = User(
        full_name='user 2',
        username='user2',
        email='user2@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
        location='UK',
        seller=False
    )
    q_u1 = User.query.filter_by(username='user1').first()
    q_u2 = User.query.filter_by(username='user2').first()
    if q_u1 is None:
        db.session.add(u1)
    if q_u2 is None:
        db.session.add(u2)

    db.session.commit()


def add_cat():

    category_a = Category(
        name="DSLR cameras"
    )

    category_b = Category(
        name="Lenses"
    )
    category_c = Category(
        name="Video cameras"
    )

    category_d = Category(
        name="Compact cameras"

    )
    category_e = Category(
        name="Flashguns"

    )
    category_f = Category(
        name="Action cameras"

    )
    category_g = Category(
        name="Photo and Video accessories"

    )

    q_category_a = Category.query.filter_by(
        name='DSLR cameras').first()
    q_category_b = Category.query.filter_by(
        name='Lenses').first()
    q_category_c = Category.query.filter_by(
        name='Video cameras').first()
    q_category_d = Category.query.filter_by(
        name='Compact cameras').first()
    q_category_e = Category.query.filter_by(
        name='Flashguns').first()
    q_category_f = Category.query.filter_by(
        name='Action cameras').first()
    q_category_g = Category.query.filter_by(
        name='Photo and Video accessories').first()

    if q_category_a is None:
        db.session.add(category_a)
    if q_category_b is None:
        db.session.add(category_b)
    if q_category_c is None:
        db.session.add(category_c)
    if q_category_d is None:
        db.session.add(category_d)
    if q_category_e is None:
        db.session.add(category_e)
    if q_category_f is None:
        db.session.add(category_f)
    if q_category_g is None:
        db.session.add(category_g)
    db.session.flush()
    db.session.commit()


def add_item():
    u1 = User.query.filter_by(username='user1').first()
    u2 = User.query.filter_by(username='user2').first()
    category_a = Category.query.filter_by(name='DSLR cameras').first()
    category_b = Category.query.filter_by(name='Lenses').first()
    category_c = Category.query.filter_by(name='Video cameras').first()
    category_d = Category.query.filter_by(name='Compact cameras').first()
    category_e = Category.query.filter_by(name='Flashguns').first()
    category_f = Category.query.filter_by(name='Action cameras').first()
    category_g = Category.query.filter_by(
        name='Photo and Video accessories').first()

    item_a = Item(
        title="item 1",
        description="something about the item 1",
        item_location="UK",
        condition="Used",
        price="10",
        owner=u1,
        category=category_a
    )

    item_b = Item(
        title="item 2",
        description="something about the item 2",
        item_location="USA",
        condition="Used",
        price="20",
        owner=u2,
        category=category_b,

    )
    item_c = Item(
        title="Item 3 ",
        description="something about the item 3",
        item_location="Spain",
        condition="For parts or not working",
        price="50",
        owner=u1,
        category=category_c,
        sold=True
    )

    item_d = Item(
        title="item 4",
        description="something about the item 4",
        item_location="Germany",
        condition="Like new",
        price="70",
        owner=u2,
        category=category_d,
        sold=True

    )

    q_item_b = Item.query.filter_by(
        title='item_b').first()
    q_item_a = Item.query.filter_by(
        title='item_a').first()
    q_item_c = Item.query.filter_by(
        title='item_c').first()
    q_item_d = Item.query.filter_by(
        title='item_d').first()

    if q_item_a is None:
        db.session.add(item_a)
    if q_item_b is None:
        db.session.add(item_b)
    if q_item_c is None:
        db.session.add(item_c)
    if q_item_d is None:
        db.session.add(item_d)
    db.session.flush()
    db.session.commit()


if __name__ == '__main__':
    add_user()
    add_cat()
    add_item()
