from project.app import db
from project.models import Flaskr, User

# create the database and the db table
db.create_all()
db.session.add(User('admin', 'admin@', 'admin'))
# commit the changes
db.session.commit()

# adding admin user
