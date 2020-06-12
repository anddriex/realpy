import json
import os
import unittest
from unittest.mock import patch

import models
from app import app, db

TEST_DB = "test.db"


class BasicTestCase(unittest.TestCase):
    def test_index(self):
        """initial test. ensure flask was set up correctly"""
        tester = app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertEqual(response.status_code, 200)

    def test_database(self):
        tester = os.path.exists("flaskr.db")
        self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):
    mock_busi_file_data = {
        'id': 'jedi1',
        'name': 'namecusein.pdf'
    }

    mock_values = [
        {
            'id': 'jedi1',
            'name': 'namecusein.pdf'
        },
        {
            'id': 'sith',
            'name': 'revenge.docx'
        },
    ]

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
        return self.app.post(
            "/login",
            data=dict(username=username, password=password),
            follow_redirects=True,
        )

    def logout(self):
        """Logout helper function"""
        return self.app.get("/logout", follow_redirects=True)

    def post_new_message(self, title_msg, text_msg):
        with patch('app.get_user_files') as mocked_get_user_files:
            mocked_get_user_files.return_value = self.mock_values
            self.login(app.config["USERNAME"], app.config["PASSWORD"])
            return self.app.post(
                "/add", data=dict(title=title_msg, text=text_msg), follow_redirects=True
            )

    def add_new_specialist_user(self, usr_name, usr_email, usr_password,
                                pro_experience, pro_speciality):
        return self.app.post('/add_specialist', data=json.dumps(dict(username=usr_name, email=usr_email,
                                                                     password=usr_password, experience=pro_experience,
                                                                     speciality=pro_speciality)),
                             content_type='application/json')

    # assert functions

    def test_empty_db(self):
        """Ensure database is blank"""
        rv = self.app.get("/")
        self.assertIn(b"No hay entradas. Agrega una ahora!", rv.data)

    @patch('app.get_user_files')
    def test_login_logout(self, mocked_get_user_files):
        """Test login and logout using helper functions."""
        mocked_get_user_files.return_value = self.mock_values
        rv = self.login(app.config["USERNAME"], app.config["PASSWORD"])
        self.assertIn(b"Has iniciado sesi\xc3\xb3n", rv.data)
        rv = self.logout()
        self.assertIn(b"Sesi\xc3\xb3n cerrada exitosamente", rv.data)
        rv = self.login(app.config["USERNAME"] + "x", app.config["PASSWORD"])
        self.assertIn(b"Nombre de usuario invalida", rv.data)
        rv = self.login(app.config["USERNAME"], app.config["PASSWORD"] + "x")
        self.assertIn(b"Password invalido", rv.data)

    def test_messages(self):
        """Ensure that a user can post messages."""
        rv = self.post_new_message(
            title_msg="<Hello>", text_msg="<strong>HTML</strong> allowed here"
        )
        self.assertNotIn(b"No hay entradas. Agrega una ahora!", rv.data)
        self.assertIn(b"&lt;Hello&gt;", rv.data)
        self.assertIn(b"<strong>HTML</strong> allowed here", rv.data)

    def test_edit_message(self):
        """Ensure the messages are being editing"""
        self.post_new_message("hello", "hru")
        rv = self.app.get("/edit/1")
        self.assertIn(b"Editar post", rv.data)
        self.assertIn(b"hello", rv.data)
        self.assertIn(b"hru", rv.data)
        rv = self.app.post(
            "/edit/1", data=dict(title="Bye", text="doom"), follow_redirects=True
        )
        self.assertIn(b"Entrada actualizada!", rv.data)
        self.assertIn(b"Bye", rv.data)
        self.assertIn(b"doom", rv.data)

    @patch('app.get_user_files')
    def test_delete_message(self, mocked_get_user_files):
        """Ensure the messages are being deleted."""
        mocked_get_user_files.return_value = self.mock_values
        self.login(app.config["USERNAME"], app.config["PASSWORD"])
        rv = self.app.get("/delete/1", follow_redirects=True)
        self.assertIn(b"No hay entradas. Agrega una ahora!", rv.data)

    def test_search_posts(self):
        """Ensure to messages are being queried"""
        self.post_new_message(
            title_msg="<Hello>", text_msg="<strong>HTML</strong> allowed here"
        )
        self.post_new_message(
            title_msg="<GoodBye>", text_msg="<strong>HTML</strong> allowed here"
        )
        rv = self.app.get("/search?query=Hello")
        self.assertIn(b"&lt;Hello&gt;", rv.data)
        self.assertNotIn(b"&lt;GoodBye&gt;", rv.data)

    def test_delete_message_only_for_registered_user(self):
        """Ensure only registered users can delete messages"""
        rv = self.app.get("/delete/1", follow_redirects=True)
        self.assertIn(b"Please log in.", rv.data)

    @patch('app.get_user_file')
    def test_get_case(self, mock_get_user_file):
        mock_get_user_file.return_value = self.mock_busi_file_data
        rv = self.app.get('case/jedi1', follow_redirects=True)
        self.assertIn(b'type', rv.data)
        self.assertIn(b'namecusein', rv.data)

    @patch('app.get_user_file')
    def test_add_businessfile_type(self, mock_get_user_file):
        mock_get_user_file.return_value = self.mock_busi_file_data
        self.app.post('/case/jedi1',
                      data={'type': 'Public', 'name': 'cusein'})
        self.assertEqual(db.session.query(models.BusinessFile).count(), 1)
        bf = db.session.query(models.BusinessFile).first()
        self.assertEqual(bf.gdrive_id, 'jedi1')
        self.assertEqual(bf.type, 'Public')
        self.assertEqual(bf.status, 'disponible')
        self.assertEqual(bf.name, 'cusein.pdf')

    @patch('app.get_user_files')
    @patch('app.get_user_file')
    def test_list_available_cases(self, mock_get_user_file, mocked_get_user_files):
        mocked_get_user_files.return_value = self.mock_values
        self.login(app.config["USERNAME"], app.config["PASSWORD"])

        mock_get_user_file.return_value = self.mock_values[0]
        self.app.post('/case/jedi1', data={'type': 'Public', 'name': 'namecusein'})

        rv = self.app.get('/files', follow_redirects=True)
        self.assertIn(b'revenge', rv.data)
        self.assertNotIn(b'namecusein', rv.data)

    @patch('app.get_user_files')
    @patch('app.get_user_file')
    def test_list_business_files(self, mock_get_user_file, mocked_get_user_files):
        mock_get_user_file.return_value = self.mock_busi_file_data
        mocked_get_user_files.return_value = self.mock_values

        self.login(app.config["USERNAME"], app.config["PASSWORD"])

        self.app.post('/case/jedi1',
                      data={'type': 'Public', 'name': 'cusein'})
        rv = self.app.get('/bfiles/')
        self.assertIn(b'cusein', rv.data)
        self.assertIn(b'Public', rv.data)
        self.assertIn(b'disponible', rv.data)

    def test_add_specialist(self):
        self.add_new_specialist_user(usr_name='andres',
                                     usr_email='a@a',
                                     usr_password='hello',
                                     pro_experience=2,
                                     pro_speciality='patentes')
        self.assertEqual(db.session.query(models.Professional).count(), 1)
        self.assertEqual(db.session.query(models.User).count(), 1)
        usr = db.session.query(models.User).first()
        self.assertEqual(usr.username, 'andres')
        self.assertEqual(usr.email, 'a@a')
        self.assertEqual(usr.password, 'hello')
        pro = usr.speciality
        self.assertEqual(pro.experience, 2)
        self.assertEqual(pro.speciality, 'patentes')

    @patch('app.get_user_files')
    @patch('app.get_user_file')
    def test_list_specialists_for_file(self, mock_get_user_file, mocked_get_user_files):
        mocked_get_user_files.return_value = self.mock_values
        self.login(app.config["USERNAME"], app.config["PASSWORD"])

        self.add_new_specialist_user(usr_name='andres',
                                     usr_email='a@a',
                                     usr_password='hello',
                                     pro_experience=2,
                                     pro_speciality='patentes')
        self.add_new_specialist_user(usr_name='maria',
                                     usr_email='m@a',
                                     usr_password='hello',
                                     pro_experience=3,
                                     pro_speciality='patentes')
        self.add_new_specialist_user(usr_name='jorge',
                                     usr_email='j@a',
                                     usr_password='hello1',
                                     pro_experience=4,
                                     pro_speciality='derechos laborales')
        mock_get_user_file.return_value = self.mock_busi_file_data
        self.app.post('/case/jedi1',
                      data={'type': 'patentes', 'name': 'cusein'})
        mock_get_user_file.return_value = {
            'id': 'jedi2',
            'name': 'loqe'
        }
        self.app.post('/case/jedi2',
                      data={'type': 'derechos laborales', 'name': 'pluton'})
        rv = self.app.get('bfiles/1', follow_redirects=True)
        self.assertIn(b'maria', rv.data)
        self.assertIn(b'andres', rv.data)
        self.assertNotIn(b'jorge', rv.data)
        rv = self.app.get('bfiles/2', follow_redirects=True)
        self.assertNotIn(b'maria', rv.data)
        self.assertNotIn(b'andres', rv.data)
        self.assertIn(b'jorge', rv.data)

    @patch('app.get_user_files')
    @patch('app.get_user_file')
    def test_assign_specialist_for_file(self, mock_get_user_file, mocked_get_user_files):
        mocked_get_user_files.return_value = self.mock_values
        self.login(app.config["USERNAME"], app.config["PASSWORD"])
        self.add_new_specialist_user(usr_name='andres',
                                     usr_email='a@a',
                                     usr_password='hello',
                                     pro_experience=2,
                                     pro_speciality='patentes')
        mock_get_user_file.return_value = self.mock_busi_file_data
        self.app.post('/case/jedi1',
                      data={'type': 'patentes', 'name': 'cusein'})
        rv = self.app.get('/assign_alligator/1/1', follow_redirects=True)
        self.assertIn(b'cusein', rv.data)
        self.assertIn(b'patentes', rv.data)
        self.assertIn(b'en curso', rv.data)


if __name__ == "__main__":
    unittest.main()
