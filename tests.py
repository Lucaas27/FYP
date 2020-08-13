from datetime import datetime, timedelta
import unittest
from app import app, db, bcrypt
from app.models import *


class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(
            first_name='user',
            last_name='1',
            username='user',
            email='user@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'cat').decode("utf-8")
        )
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_follow(self):
        u1 = User(
            first_name='user',
            last_name='1',
            username='user1',
            email='user1@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )
        u2 = User(
            first_name='user',
            last_name='2',
            username='user2',
            email='user2@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'user2')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'user1')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def add_cat(self):

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

        db.session.add_all([category_a, category_b, category_c,
                            category_d, category_e, category_f, category_g])
        db.session.commit()

    def test_follow_items(self):
        category_a = Category.query.filter_by(name='DSLR cameras').first()
        category_b = Category.query.filter_by(name='Lenses').first()
        category_c = Category.query.filter_by(name='Video cameras').first()
        category_d = Category.query.filter_by(name='Compact cameras').first()
        # create four users
        u1 = User(
            first_name='user',
            last_name='1',
            username='user1',
            email='user1@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )
        u2 = User(
            first_name='user',
            last_name='2',
            username='user2',
            email='user2@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )
        u3 = User(
            first_name='user',
            last_name='3',
            username='user3',
            email='user3@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )
        u4 = User(
            first_name='user',
            last_name='4',
            username='user4',
            email='user4@gmail.com',
            password_hash=bcrypt.generate_password_hash(
                'password').decode("utf-8")
        )

        db.session.add_all([u1, u2, u3, u4])

        # create four Item for sale
        now = datetime.utcnow()
        item_1 = ItemForSale(
            title="item 1",
            description="something about the item 1",
            item_city="london",
            condition="Used",
            price="10.0",
            created_at=now + timedelta(seconds=1),
            seller=u1,
            category=category_a
        )
        item_2 = ItemForSale(
            title="item 2",
            description="something about the item 2",
            item_city="leicester",
            condition="Used",
            price="50.0",
            created_at=now + timedelta(seconds=4),
            seller=u2,
            category=category_b
        )
        item_3 = ItemForSale(
            title="item 3",
            description="something about the item 3",
            item_city="bristol",
            condition="Used",
            price="70.0",
            created_at=now + timedelta(seconds=3),
            seller=u3,
            category=category_c
        )
        item_4 = ItemForSale(
            title="item 4",
            description="something about the item 4",
            item_city="london",
            condition="Used",
            price="80.0",
            created_at=now + timedelta(seconds=2),
            seller=u4,
            category=category_d
        )

        db.session.add_all([item_1, item_2, item_3, item_4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # user1 follows user2
        u1.follow(u4)  # user1 follows user4
        u2.follow(u3)  # user2 follows user3
        u3.follow(u4)  # user3 follows user4
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_items().all()
        f2 = u2.followed_items().all()
        f3 = u3.followed_items().all()
        f4 = u4.followed_items().all()
        self.assertEqual(f1, [item_4, item_2])
        self.assertEqual(f2, [item_3])
        self.assertEqual(f3, [item_4])
        self.assertEqual(f4, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
