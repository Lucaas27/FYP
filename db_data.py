from app import db, models, bcrypt
from app.models import User, ItemForSale, Category, Address, followers, user_addresses
from datetime import datetime


def add_user():

    admin = User(
        first_name='Lucas',
        last_name='Gomes',
        username='admin',
        email='admin@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
    )

    u1 = User(
        first_name='user',
        last_name='1',
        username='user1',
        email='user1@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
    )
    u2 = User(
        first_name='user',
        last_name='2',
        username='user2',
        email='user2@gmail.com',
        password_hash=bcrypt.generate_password_hash(
            'password').decode("utf-8"),
    )
    q_u1 = User.query.filter_by(username='user1').first()
    q_u2 = User.query.filter_by(username='user2').first()
    q_admin = User.query.filter_by(username='admin').first()
    if q_u1 is None:
        db.session.add(u1)
    if q_u2 is None:
        db.session.add(u2)
    if q_admin is None:
        db.session.add(admin)

    db.session.commit()


def add_address():
    u1 = User.query.filter_by(username='user1').first()
    u2 = User.query.filter_by(username='user2').first()
    admin = User.query.filter_by(username='admin').first()
    a1 = Address(
        address='4 High street',
        post_code='LE1 1QA',
        city='Leicester',
        country='UK',
    )

    a2 = Address(
        address='2 Squirrel ln',
        post_code='PE12 9BU',
        city='Peterborough',
        country='UK',
    )

    a3 = Address(
        address='12 St. George',
        post_code='EL35TH',
        country='UK',
        city='Manchester'
    )

    a4 = Address(
        address='23 Lion street',
        post_code='MA76TR',
        country='UK',
        city='London'
    )

    a1_append = a1.user.append(u1)
    a2_append = a2.user.append(u2)
    a3_append = a3.user.append(u1)
    a4_append = a4.user.append(u2)
    a5_append = a4.user.append(admin)

    q_a1 = Address.query.filter_by(post_code='LE1 1QA').first()
    q_a2 = Address.query.filter_by(post_code='PE12 9BU').first()
    q_a3 = Address.query.filter_by(post_code='EL35TH').first()
    q_a4 = Address.query.filter_by(post_code='MA76TR').first()
    if q_a1 is None:
        db.session.add(a1)
    if q_a2 is None:
        db.session.add(a2)
    if q_a3 is None:
        db.session.add(a3)
    if q_a4 is None:
        db.session.add(a4)

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
    a1 = Address.query.filter_by(post_code='LE1 1QA').first()
    a2 = Address.query.filter_by(post_code='PE12 9BU').first()
    a3 = Address.query.filter_by(post_code='EL35TH').first()
    a4 = Address.query.filter_by(post_code='MA76TR').first()

    item_a = ItemForSale(
        title="item 1",
        description="something about the item 1",
        quantity=20,
        item_city="London",
        condition="Used",
        price="10",
        seller=u1,
        category=category_a
    )

    item_b = ItemForSale(
        title="item 2",
        description="something about the item 2",
        quantity=10,
        item_city="London",
        condition="Used",
        price="20",
        seller=u2,
        category=category_b,

    )
    item_c = ItemForSale(
        title="item 3 ",
        description="something about the item 3",
        item_city="Leicester",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_c,
    )

    item_d = ItemForSale(
        title="item 4",
        description="something about the item 4",
        quantity=5,
        item_city="Barcelona",
        condition="Like new",
        price="70",
        seller=u2,
        category=category_d,

    )
    item_e = ItemForSale(
        title="item 5",
        description="something about the item 5",
        item_city="Leeds",
        condition="Like new",
        price="70",
        seller=u1,
        category=category_e,

    )
    item_f = ItemForSale(
        title="item 6",
        description="something about the item 6",
        item_city="Nottingham",
        condition="Like new",
        price="70",
        seller=u2,
        category=category_f,

    )
    item_g = ItemForSale(
        title="item 7 ",
        description="something about the item 7",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_d,


    )
    item_h = ItemForSale(
        title="item 8 ",
        description="something about the item 8",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u2,
        category=category_c,


    )
    item_i = ItemForSale(
        title="item 9",
        description="something about the item 9",
        item_city="Birmingham",
        condition="Like new",
        price="70",
        seller=u1,
        category=category_e,

    )
    item_j = ItemForSale(
        title="item 10",
        description="something about the item 10",
        item_city="Nottingham",
        condition="Like new",
        price="70",
        seller=u2,
        category=category_f,

    )
    item_k = ItemForSale(
        title="item 11 ",
        description="something about the item 11",
        item_city="Leicester",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_d,

    )
    item_l = ItemForSale(
        title="item 12 ",
        description="something about the item 12",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u2,
        category=category_b,

    )
    item_m = ItemForSale(
        title="item 13 ",
        description="something about the item 13",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u2,
        category=category_a,

    )
    item_n = ItemForSale(
        title="item 14 ",
        description="something about the item n",
        item_city="Nottingham",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_d,

    )
    item_o = ItemForSale(
        title="item 15 ",
        description="something about the item 15",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u2,
        category=category_c,

    )
    item_p = ItemForSale(
        title="item 16 ",
        description="something about the item 16",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u2,
        category=category_c,

    )
    item_q = ItemForSale(
        title="item 17 ",
        description="something about the item 17 ",
        item_city="Leicester",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_c,

    )
    item_r = ItemForSale(
        title="item 18 ",
        description="something about the item 18",
        item_city="London",
        condition="For parts or not working",
        price="50",
        seller=u1,
        category=category_c,

    )

    q_item_b = ItemForSale.query.filter_by(
        title='item_b').first()
    q_item_a = ItemForSale.query.filter_by(
        title='item_a').first()
    q_item_c = ItemForSale.query.filter_by(
        title='item_c').first()
    q_item_d = ItemForSale.query.filter_by(
        title='item_d').first()
    q_item_e = ItemForSale.query.filter_by(
        title='item_e').first()
    q_item_f = ItemForSale.query.filter_by(
        title='item_f').first()
    q_item_g = ItemForSale.query.filter_by(
        title='item_g').first()
    q_item_h = ItemForSale.query.filter_by(
        title='item_h').first()
    q_item_i = ItemForSale.query.filter_by(
        title='item_i').first()
    q_item_j = ItemForSale.query.filter_by(
        title='item_j').first()
    q_item_k = ItemForSale.query.filter_by(
        title='item_k').first()
    q_item_l = ItemForSale.query.filter_by(
        title='item_l').first()
    q_item_m = ItemForSale.query.filter_by(
        title='item_m').first()
    q_item_n = ItemForSale.query.filter_by(
        title='item_n').first()
    q_item_o = ItemForSale.query.filter_by(
        title='item_o').first()
    q_item_p = ItemForSale.query.filter_by(
        title='item_p').first()
    q_item_q = ItemForSale.query.filter_by(
        title='item_q').first()
    q_item_r = ItemForSale.query.filter_by(
        title='item_r').first()

    if q_item_a is None:
        db.session.add(item_a)
    if q_item_b is None:
        db.session.add(item_b)
    if q_item_c is None:
        db.session.add(item_c)
    if q_item_d is None:
        db.session.add(item_d)
    if q_item_e is None:
        db.session.add(item_e)
    if q_item_f is None:
        db.session.add(item_f)
    if q_item_g is None:
        db.session.add(item_g)
    if q_item_h is None:
        db.session.add(item_h)
    if q_item_i is None:
        db.session.add(item_i)
    if q_item_j is None:
        db.session.add(item_j)
    if q_item_k is None:
        db.session.add(item_k)
    if q_item_l is None:
        db.session.add(item_l)
    if q_item_m is None:
        db.session.add(item_m)
    if q_item_n is None:
        db.session.add(item_n)
    if q_item_o is None:
        db.session.add(item_o)
    if q_item_p is None:
        db.session.add(item_p)
    if q_item_q is None:
        db.session.add(item_q)
    if q_item_r is None:
        db.session.add(item_r)

    db.session.flush()
    db.session.commit()


if __name__ == '__main__':
    add_user()
    add_address()
    add_cat()
    add_item()
