from .app import db
from sqlalchemy.orm import relationship


class Flaskr(db.Model):
    __tablename__ = "flaskr"

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=False)

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return f"<title {self.body}>"


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    speciality = relationship('Professional', uselist=False, back_populates='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password



class Professional(db.Model):
    __tablename__ = 'professional'
    id = db.Column(db.Integer, primary_key=True)
    experience = db.Column(db.Integer, nullable=False)
    speciality = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='speciality')

    def __init__(self, experience, speciality):
        self.experience = experience
        self.speciality = speciality


class BusinessFile(db.Model):
    __tablename__ = 'business_file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    gdrive_id = db.Column(db.String, nullable=False)
    type = db.Column(db.String)
    status = db.Column(db.String, nullable=False)

    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'))
    reviewer = relationship('Professional', back_populates='files')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = relationship('User', back_populates='cases')

    def __init__(self, gdrive_id, type, name, status):
        self.name = name
        self.gdrive_id = gdrive_id
        self.type = type
        self.status = status


Professional.files = relationship('BusinessFile',
                                  order_by=BusinessFile.id,
                                  back_populates='reviewer')
User.cases = relationship('BusinessFile',
                          order_by=BusinessFile.id,
                          back_populates='owner')


def get_businessfiles(user_files):
    return list(filter(lambda file: not db.session.query(BusinessFile).filter_by(gdrive_id=file['id']).first(),
                       user_files))
