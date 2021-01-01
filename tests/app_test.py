import pytest
import json

import project.models as models
from project.app import app, db
from pathlib import Path
from flask import current_app

TEST_DB = "test.db"

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


@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config['TESTING'] = True
    app.config['DATABASE'] = BASE_DIR.joinpath(TEST_DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR.joinpath(TEST_DB)}'
    db.create_all()
    yield app.test_client()
    db.drop_all()


def login(client, username, password):
    """Login helper function."""

    with app.app_context():
        assert current_app.config['USERNAME'] == 'admin'

    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Logout helper function"""
    return client.get("/logout", follow_redirects=True)


def post_new_message(client, title_msg, text_msg, mocker):
    mocker.patch('project.app.get_user_files', return_value=mock_values)
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    return client.post(
        "/add", data=dict(title=title_msg, text=text_msg), follow_redirects=True
    )


def add_new_specialist_user(client, usr_name, usr_email, usr_password,
                            pro_experience, pro_speciality):
    return client.post('/add_specialist', data=json.dumps(dict(username=usr_name, email=usr_email,
                                                               password=usr_password, experience=pro_experience,
                                                               speciality=pro_speciality)),
                       content_type='application/json')


def test_index(client):
    """initial test. ensure flask was set up correctly"""
    response = client.get('/', content_type="html/text")
    assert response.status_code == 200


def test_database():
    """initial test. ensure that the database exists"""
    db.create_all()
    assert Path("test.db").is_file()


def test_empty_db(client):
    """Ensure database is blank"""
    rv = client.get("/")
    assert b"No hay entradas. Agrega una ahora!" in rv.data


def test_login_logout(client, mocker):
    """Test login and logout using helper functions."""
    mocker.patch('project.app.get_user_files', return_value=mock_values)
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"Has iniciado sesi\xc3\xb3n" in rv.data
    rv = logout(client)
    assert b"Sesi\xc3\xb3n cerrada exitosamente" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Nombre de usuario invalida" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Password invalido" in rv.data


def test_messages(client, mocker):
    """Ensure that a user can post messages."""
    rv = post_new_message(client,
                          title_msg="<Hello>", text_msg="<strong>HTML</strong> allowed here",
                          mocker=mocker)
    assert b"No hay entradas. Agrega una ahora!" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


def test_edit_message(client, mocker):
    """Ensure the messages are being editing"""
    post_new_message(client, "hello", "hru", mocker)
    rv = client.get("/edit/1")
    assert b"Editar post" in rv.data
    assert b"hello" in rv.data
    assert b"hru" in rv.data
    rv = client.post(
        "/edit/1", data=dict(title="Bye", text="doom"), follow_redirects=True
    )
    assert b"Entrada actualizada!" in rv.data
    assert b"Bye" in rv.data
    assert b"doom" in rv.data


def test_delete_message(client, mocker):
    """Ensure the messages are being deleted."""
    mocker.patch('project.app.get_user_files', return_value = mock_values)
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/delete/1", follow_redirects=True)
    assert b"No hay entradas. Agrega una ahora!" in rv.data


def test_search_posts(client, mocker):
    """Ensure to messages are being queried"""
    post_new_message(client,
                     title_msg="<Hello>", text_msg="<strong>HTML</strong> allowed here",
                     mocker=mocker)
    post_new_message(client,
                     title_msg="<GoodBye>", text_msg="<strong>HTML</strong> allowed here",
                     mocker=mocker)
    rv = client.get("/search?query=Hello")
    assert b"&lt;Hello&gt;" in rv.data
    assert b"&lt;GoodBye&gt;" not in rv.data


def test_delete_message_only_for_registered_user(client):
    """Ensure only registered users can delete messages"""
    rv = client.get("/delete/1", follow_redirects=True)
    assert b"Please log in." in rv.data


def test_get_case(client, mocker):
    mocker.patch('project.app.get_user_file', return_value=mock_busi_file_data)
    rv = client.get('case/jedi1', follow_redirects=True)
    assert b'type' in rv.data
    assert b'namecusein' in rv.data


def test_add_businessfile_type(client, mocker):
    mocker.patch('project.app.get_user_file', return_value=mock_busi_file_data)
    client.post('/case/jedi1',
                data={'type': 'Public', 'name': 'cusein'})
    assert db.session.query(models.BusinessFile).count() == 1
    bf = db.session.query(models.BusinessFile).first()
    assert bf.gdrive_id == 'jedi1'
    assert bf.type == 'Public'
    assert bf.status == 'disponible'
    assert bf.name == 'cusein.pdf'


def test_list_available_cases(client, mocker):
    mocker.patch('project.app.get_user_files', return_value=mock_values)
    login(client, app.config["USERNAME"], app.config["PASSWORD"])

    mocker.patch('project.app.get_user_file', return_value=mock_values[0])
    client.post('/case/jedi1', data={'type': 'Public', 'name': 'namecusein'})

    rv = client.get('/files', follow_redirects=True)
    assert b'revenge' in rv.data
    assert b'namecusein' not in rv.data



def test_list_business_files(client, mocker):
    mocker.patch('project.app.get_user_file', return_value=mock_busi_file_data)
    mocker.patch('project.app.get_user_files', return_value=mock_values)

    login(client, app.config["USERNAME"], app.config["PASSWORD"])

    client.post('/case/jedi1',
                data={'type': 'Public', 'name': 'cusein'})
    rv = client.get('/bfiles/')
    assert b'cusein' in rv.data
    assert b'Public' in rv.data
    assert b'disponible' in rv.data


def test_add_specialist(client):
    add_new_specialist_user(client,
                            usr_name='andres',
                            usr_email='a@a',
                            usr_password='hello',
                            pro_experience=2,
                            pro_speciality='patentes')
    assert db.session.query(models.Professional).count() == 1
    assert db.session.query(models.User).count() == 1
    usr = db.session.query(models.User).first()
    assert usr.username == 'andres'
    assert usr.email == 'a@a'
    assert usr.password == 'hello'
    pro = usr.speciality
    assert pro.experience == 2
    assert pro.speciality == 'patentes'


def test_list_specialists_for_file(client, mocker):
    mocker.patch('project.app.get_user_files', return_value=mock_values)
    login(client, app.config["USERNAME"], app.config["PASSWORD"])

    add_new_specialist_user(client,
                            usr_name='andres',
                            usr_email='a@a',
                            usr_password='hello',
                            pro_experience=2,
                            pro_speciality='patentes')
    add_new_specialist_user(client,
                            usr_name='maria',
                            usr_email='m@a',
                            usr_password='hello',
                            pro_experience=3,
                            pro_speciality='patentes')
    add_new_specialist_user(client,
                            usr_name='jorge',
                            usr_email='j@a',
                            usr_password='hello1',
                            pro_experience=4,
                            pro_speciality='derechos laborales')
    mocker.patch('project.app.get_user_file', return_value=mock_busi_file_data)

    client.post('/case/jedi1',
                data={'type': 'patentes', 'name': 'cusein'})
    mocker.patch('project.app.get_user_file', return_value={
        'id': 'jedi2',
        'name': 'loqe'
    })
    client.post('/case/jedi2',
                data={'type': 'derechos laborales', 'name': 'pluton'})
    rv = client.get('bfiles/1', follow_redirects=True)
    assert b'maria' in rv.data
    assert b'andres' in rv.data
    assert b'jorge' not in rv.data
    rv = client.get('bfiles/2', follow_redirects=True)
    assert b'maria' not in rv.data
    assert b'andres' not in rv.data
    assert b'jorge' in rv.data


def test_assign_specialist_for_file(client, mocker):
    mocker.patch('project.app.get_user_files', return_value=mock_values)

    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    add_new_specialist_user(client,
                            usr_name='andres',
                            usr_email='a@a',
                            usr_password='hello',
                            pro_experience=2,
                            pro_speciality='patentes')
    mocker.patch('project.app.get_user_file', return_value=mock_busi_file_data)
    client.post('/case/jedi1',
                data={'type': 'patentes', 'name': 'cusein'})
    rv = client.get('/assign_alligator/1/1', follow_redirects=True)
    assert b'cusein' in rv.data
    assert b'patentes' in rv.data
    assert b'en curso' in rv.data
