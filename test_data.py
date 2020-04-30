from app import db, models, bcrypt
from datetime import datetime


def add_user():
    u1 = models.User(
        full_name='user 1',
        username='user1',
        email='user1@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
        location='UK'
    )
    u2 = models.User(
        full_name='user 2',
        username='user2',
        email='user2@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
        location='UK'
    )
    q_u1 = models.User.query.filter_by(username='user1').first()
    q_u2 = models.User.query.filter_by(username='user2').first()
    if q_u1 is None:
        db.session.add(u1)
    if q_u2 is None:
        db.session.add(u2)

    db.session.commit()


def add_item():
    u1 = models.User.query.filter_by(username='user1').first()
    u2 = models.User.query.filter_by(username='user2').first()

    item_a = models.Item(
        title="item 1",
        description="something about the item 1",
        item_location="UK",
        condition="good condition",
        price="10",
        category="camera",
        owner=u1
    )

    item_b = models.Item(
        title="item 2",
        description="something about the item 2",
        item_location="USA",
        condition="very bad condition",
        price="20",
        category="Lenses",
        owner=u2,

    )
    item_c = models.Item(
        title="Item 3 ",
        description="something about the item 3",
        item_location="Spain",
        condition="no problems",
        price="50",
        category="camera",
        owner=u1,
        sold=True
    )

    item_d = models.Item(
        title="item 4",
        description="something about the item 4",
        item_location="Germany",
        condition="bad condition",
        price="70",
        category="Lenses",
        owner=u2,
        sold=True

    )

    q_item_b = models.Item.query.filter_by(
        title='item_b').first()
    q_item_a = models.Item.query.filter_by(
        title='item_a').first()
    q_item_c = models.Item.query.filter_by(
        title='item_c').first()
    q_item_d = models.Item.query.filter_by(
        title='item_d').first()

    if q_item_a is None:
        db.session.add(item_a)
    if q_item_b is None:
        db.session.add(item_b)
    if q_item_c is None:
        db.session.add(item_c)
    if q_item_d is None:
        db.session.add(item_d)

    db.session.commit()


if __name__ == '__main__':
    add_user()
    add_item()
