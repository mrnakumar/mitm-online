import os

from flask import Flask
from flask import g
from flask import render_template
from flask import request, redirect, url_for
import database
import uuid
import admin_service
from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from models import User
app = Flask(__name__)
app.secret_key = uuid.uuid4().bytes
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db_name = os.environ.get("db_name") or ":memory:"
admin_service = admin_service.DatabaseService()

@app.route("/")
@login_required
def home():
    return render_template('home.html')

@app.route("/blocked")
@login_required
def blocked():
    return admin_service.get_blocked(get_db())

@app.route("/browsed")
@login_required
def browsed():
    return admin_service.get_browsed(get_db())

@app.route("/ignored")
@login_required
def ignored():
    return admin_service.get_ignored(get_db())

@app.route("/block_hostname", methods = ["POST"])
@login_required
def block_hostname():
    hostname_to_block = request.form['hostname']
    db = get_db()
    target = get_target(request)
    admin_service.block_hostname(db, hostname_to_block)
    return redirect(url_for(target), 303)

@app.route("/unblock_hostname", methods = ["POST"])
@login_required
def unblock_hostname():
    hostname_to_unblock = request.form['hostname']
    db = get_db()
    admin_service.unblock_hostname(db, hostname_to_unblock)
    return redirect(url_for('blocked'), 303)

@app.route("/ignore_hostname", methods= ["POST"])
@login_required
def ignore_hostname():
    hostname_to_ignore = request.form['hostname']
    db = get_db()
    target = get_target(request)
    admin_service.ignore_hostname(db, hostname_to_ignore)
    return redirect(url_for(target), 303)

@app.route("/unignore_hostname", methods = ["POST"])
@login_required
def unignore_hostname():
    hostname_to_unignore = request.form['hostname']
    db = get_db()
    admin_service.unignore_hostname(db, hostname_to_unignore)
    return redirect(url_for('ignored'), 303)

def get_target(request):
    target = request.form.get('from')
    if target not in ['blocked', 'browsed', 'ignored']:
        target = 'home'
    return target

def get_db():
    if 'db' not in g:
        g.db = database.Database(db_name)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    user = User.load(get_db(), user_id)
    if user is not None and user.password == password:
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
    return User.load(get_db(), user_id)
