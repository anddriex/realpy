import os
import unittest
import json

from app import app, db

TEST_DB = 'test.db'


class BasicTestCase(unittest.TestCase):

    def test_index(self):
        """initial test. ensure flask was set up correctly"""
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database(self):
        tester = os.path.exists('flaskr.db')
        self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a blank temp database before each test."""
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """Destroy blank temp database after each test."""
        db.drop_all()

    def login(self, username, password):
        """Login helper function."""
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Logout helper function"""
        return self.app.get('/logout', follow_redirects=True)

    def post_new_message(self, title_msg, text_msg):
        self.login(app.config['USERNAME'], app.config['PASSWORD'])
        return self.app.post('/add', data=dict(
            title=title_msg,
            text=text_msg
        ), follow_redirects=True)

    # assert functions

    def test_empty_db(self):
        """Ensure database is blank"""
        rv = self.app.get('/')
        self.assertIn(b'No entries yet. Add some!', rv.data)

    def test_login_logout(self):
        """Test login and logout using helper functions."""
        rv = self.login(app.config['USERNAME'], app.config['PASSWORD'])
        self.assertIn(b'You were logged in', rv.data)
        rv = self.logout()
        self.assertIn(b'Sesion cerrada exitosamente', rv.data)
        rv = self.login(app.config['USERNAME'] + 'x', app.config['PASSWORD'])
        self.assertIn(b'Invalid username', rv.data)
        rv = self.login(app.config['USERNAME'], app.config['PASSWORD'] + 'x')
        self.assertIn(b'Invalid password', rv.data)

    def test_messages(self):
        """Ensure that a user can post messages."""
        rv = self.post_new_message(title_msg='<Hello>', text_msg='<strong>HTML</strong> allowed here')
        self.assertNotIn(b'No entries yet. Add some!', rv.data)
        self.assertIn(b'&lt;Hello&gt;', rv.data)
        self.assertIn(b'<strong>HTML</strong> allowed here', rv.data)

    def test_edit_message(self):
        """Ensure the messages are being editing"""
        self.post_new_message('hello', 'hru')
        rv = self.app.get('/edit/1')
        self.assertIn(b'Editar post', rv.data)
        self.assertIn(b'hello', rv.data)
        self.assertIn(b'hru', rv.data)
        rv = self.app.post('/edit/1',
                           data=dict(title='Bye', text='doom'),
                           follow_redirects=True)
        self.assertIn(b'Entrada actualizada!', rv.data)
        self.assertIn(b'Bye', rv.data)
        self.assertIn(b'doom', rv.data)

    def test_delete_message(self):
        """Ensure the messages are being deleted."""
        rv = self.app.get('/delete/1', follow_redirects=True)
        self.assertIn(b'No entries yet. Add some!', rv.data)


if __name__ == '__main__':
    unittest.main()
