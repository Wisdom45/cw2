import unittest
from app import app
from app import db
from flask import current_app
from app.models import User, Post, Comment, Permission, AnonymousUser, Role, Follow
from flask_login import login_user, logout_user, login_required, current_user
class TestModelAndLink(unittest.TestCase):
    def setUp(self):
        app.client=app.test_client()
        app.debug=True
        app_ctx = app.app_context()
        app_ctx.push()

    def tearDown(self):
        pass

    def test_password_setter(self):
        u = User(password='123456')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='123456')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='123456')
        self.assertTrue(u.verify_password('123456'))
        self.assertFalse(u.verify_password('654321'))

    def test_password_salts_are_random(self):
        u = User(password='123456')
        u2 = User(password='123456')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_user_role(self):
        u = User.query.filter_by(role_id=1).first()
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))


    def test_administrator_role(self):
        u = User.query.filter_by(role_id=3).first()
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertTrue(u.can(Permission.MODERATE_COMMENTS))
        self.assertTrue(u.can(Permission.ADMINISTER))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
        self.assertFalse(u.can(Permission.ADMINISTER))

    def test_follow(self):
        u1 = User.query.filter_by(id=1).first()
        u2 = User.query.filter_by(id=2).first()

        u1.follow(u2)
        db.session.commit()
        f = Follow.query.filter_by(follower_id=u1.id).first()
        self.assertIsNotNone(f)

    def test_user(self):
        user=User(name="test",password="test")
        db.session.add(user)
        db.session.commit()
        user=User.query.filter_by(name="test").first()
        self.assertIsNotNone(user)
        db.session.delete(user)
        db.session.commit()

    def test_post(self):
        user=User.query.filter_by(name='test').first()
        post=Post(title="Test post",body="Test post",author=user)
        db.session.add(post)
        db.session.commit()
        post=Post.query.filter_by(title="Test post").first()
        self.assertIsNotNone(post)
        db.session.delete(post)
        db.session.commit()

    def test_comment(self):
        user=User.query.filter_by(name='test').first()
        post=Post.query.filter_by(title='Test post').first()
        comment=Comment(content="Test comment",author=user,post=post)
        db.session.add(comment)
        db.session.commit()
        comment=Comment.query.filter_by(content="Test comment").first()
        self.assertIsNotNone(comment)
        db.session.delete(comment)
        db.session.commit()

    def test_register(self):
        response =app.client.get('/register',data={
            'email': 'wisdom@my.swjtu.deu',
            'username': 'Wisdom',
            'password': '123456',
            'password2': '123456'
        })
        self.assertEqual(response.status_code,200)

    def test_login(self):
        response =app.client.post('/login',data={
                'name':'sc16h3w@leeds.ac.uk',
                'password':'dzngzvm1'})
        self.assertEqual(response.status_code,200)


    def test_create_blog(self):
        response =app.client.post('/write_blog',data={
                'title':'test',
                'body':'test create blog'})
        self.assertEqual(response.status_code,200)

    def test_add_comment(self):
        response =app.client.post('/comment/1',data={
                'body':'Test comment'})
        self.assertEqual(response.status_code,200)



if __name__=='__main__':
    unittest.main()
