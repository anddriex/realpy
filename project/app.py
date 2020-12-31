# imports
import json
import os

from functools import wraps

from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    abort,
    render_template,
    flash,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, text
from project.google_drive.gdrive_service import get_user_files, get_user_file

# get the folder where this file runs
basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
SECRET_KEY = "my_precious"
USERNAME = "admin"
PASSWORD = "admin"

# database config
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL", f'sqlite:///{os.path.join(basedir, "flaskr.db")}'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# create and initialize app
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

import project.models as models

STATUS = [
    'patente',
    'derecho',
    'laboral',
    'publico'
]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Flaskr)
    print(type(entries))
    return render_template("index.html", entries=entries)


@app.route('/files')
def files():
    new_user_files = models.get_businessfiles(get_user_files())
    return render_template('profile.html',
                           files=new_user_files)


@app.route('/case/<string:gdrive_id>', methods=['GET', 'POST'])
def enter_case(gdrive_id):
    file_info = get_user_file(gdrive_id)
    if request.method == 'POST':
        print(request.form['name'])
        new_name = f"{request.form['name']}.{file_info['name'].split('.')[1]}" \
            if len(file_info['name'].split('.')) > 1 else file_info['name']
        new_bf = models.BusinessFile(gdrive_id=gdrive_id,
                                     type=request.form['type'],
                                     name=new_name,
                                     status='disponible')
        db.session.add(new_bf)
        db.session.commit()
        flash("Nueva archivo solicitado!")
        return redirect(url_for('files'))

    return render_template('case.html',
                           case={'name': file_info['name'].split('.')[0],
                                 'id': gdrive_id,
                                 'type': ''})


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == "POST":
        # query = text("SELECT * FROM user where username = '"
        #              + request.form['username'] + "' AND password = '"
        #              + request.form['password'] + "'")
        try:
            query_username = db.session.query(models.User).filter_by(username=request.form['username']).all()
            # result = db.engine.execute(query_username)
            print(query_username)
            if query_username and query_username[0].password == request.form['password']:
                session["logged_in"] = True
                flash("ÉXITO: has iniciado sesión")
                return redirect(url_for("index"))
            else:
                error = "accesos incorrectos"
        except Exception as e:
            error = e
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """User logout/authentication/session management"""
    session.pop("logged_in", None)
    flash("Sesión cerrada exitosamente")
    return redirect(url_for("index"))


@app.route("/add", methods=["POST"])
def add_entry():
    """Add new post to database."""
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Flaskr(request.form["title"], request.form["text"])
    db.session.add(new_entry)
    db.session.commit()
    flash("Nueva entrada posteada!")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    """Delete a post from database"""
    try:
        new_id = post_id
        db.session.query(models.Flaskr).filter_by(post_id=new_id).delete()
        db.session.commit()
        flash("La entrada fue eliminada")
    except Exception as e:
        flash("ERROR: ", e)

    return redirect(url_for("index"))


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_entry(post_id):
    """Edit a post from the database"""
    update_post = db.session.query(models.Flaskr).get({"post_id": post_id})
    if request.method == "POST":
        try:
            if not session.get("logged_in"):
                abort(401)
            db.session.query(models.Flaskr).filter_by(post_id=post_id).update(
                {"title": request.form["title"], "text": request.form["text"]}
            )
            db.session.commit()
            flash("Entrada actualizada!")
        except Exception as e:
            flash(e)

        return redirect(url_for("index"))
    if session.get("logged_in"):
        flash("Editar post")
    else:
        flash("Inicia sesión para editar")
    return render_template("edit.html", update_post=update_post)


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Flaskr)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")


@app.route('/bfiles/<int:bfile_id>', methods=['GET'])
@login_required
def get_business_file(bfile_id):
    busi_file = db.session.query(models.BusinessFile).get({"id": bfile_id})
    alligators_for_file = []
    if busi_file:
        for alli in db.session.query(models.Professional):
            if busi_file.type == alli.speciality:
                alligators_for_file.append({
                    'id': alli.id,
                    'name': alli.user.username,
                    'email': alli.user.email,
                    'experience': alli.experience
                })
    flash('Especialistas para archivo de negocio')
    return render_template('alligators_for_bfile.html', allis=alligators_for_file, bfile_id=bfile_id)


@app.route('/add_user', methods=['POST'])
def add_user():
    user = json.loads(request.data)
    nw_usr = models.User(user['username'], user['email'], user['password'])
    db.session.add(nw_usr)
    db.session.commit()
    flash("Nuevo usuario creado!")
    return redirect(url_for("index"))


@app.route('/bfiles/', methods=['GET'])
@login_required
def get_business_files():
    cases = db.session.query(models.BusinessFile)
    return render_template('business_files.html', bfiles=cases)


@app.route('/add_specialist', methods=['POST'])
def add_specialist():
    specialist = json.loads(request.data)
    new_usr = models.User(specialist["username"], specialist["email"], specialist["password"])
    db.session.add(new_usr)
    new_pro = models.Professional(specialist['experience'], specialist['speciality'])
    new_usr.speciality = new_pro
    db.session.add(new_pro)
    db.session.commit()
    flash("Nueva especialista agregado!")
    return redirect(url_for("index"))


@app.route('/assign_alligator/<int:professional_id>/<int:business_file_id>', methods=['GET'])
@login_required
def assign_specialist(professional_id, business_file_id):
    professional = db.session.query(models.Professional).get({"id": professional_id})
    business_file = db.session.query(models.BusinessFile).get({"id": business_file_id})
    if professional and business_file:
        business_file.reviewer = professional
        business_file.status = "en curso"
        flash('Abogado asignado!')
        db.session.commit()
    return redirect(url_for("get_business_files"))


@app.route('/report/')
def get_report():
    business_files = db.session.query(models.BusinessFile)
    dict_bf_qty = {}
    for bf in business_files:
        if not dict_bf_qty.get(bf.type):
            dict_bf_qty[bf.type] = 1
        else:
            dict_bf_qty[bf.type] += 1
    count = (0, '')
    for type in dict_bf_qty.keys():
        if dict_bf_qty.get(type) > count[0]:
            count = (dict_bf_qty.get(type), type)
    return render_template('report.html', count=count[0], type=count[1])


if __name__ == "__main__":
    app.run()
