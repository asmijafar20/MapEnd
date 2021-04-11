import unittest
from journal import app,db,bcrypt
from journal.models import User, Article
from journal.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_user(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        self.assertEqual([user1],User.query.filter_by(username="test").all())
        self.assertEqual(user1,User.query.get(1))

    def test_create_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Article(title="test blog",body="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(post1,Article.query.get(1))

    def test_users_post(self):
        user1 = User(username="test",email="test@gmail.com",password="password")
        db.session.add(user1)
        db.session.commit()
        post1 = Article(title="test blog",body="testdata",user_id=user1.id)
        db.session.add(post1)
        db.session.commit()
        self.assertEqual(user1.posts,[post1])        


if __name__ == '__main__':
    unittest.main()