import os

from flask import Flask
from flask import g
from flask import render_template
from flask import request, redirect, url_for
import database
import admin_service;
app = Flask(__name__)

db_name = os.environ.get("db_name") or ":memory:"
admin_service = admin_service.DatabaseService()

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/browsed")
def browsed():
    return admin_service.get_browsed(get_db())

@app.route("/blocked")
def blocked():
    return admin_service.get_blocked(get_db())

@app.route("/block_hostname", methods = ["POST"])
def block_hostname():
    hostname_to_block = request.form['hostname']
    db = get_db()
    admin_service.block_hostname(db, hostname_to_block)
    return redirect(url_for('browsed'), 303)

@app.route("/unblock_hostname", methods = ["POST"])
def unblock_hostname():
    hostname_to_unblock = request.form['hostname']
    db = get_db()
    admin_service.unblock_hostname(db, hostname_to_unblock)
    return redirect(url_for('blocked'), 303)

@app.route("/ignore_hostname", methods= ["POST"])
def ignore_hostname():
    hostname_to_ignore = request.form['hostname']
    origin = request.form.get('from')
    if origin not in ['browsed', 'blocked']:
        origin = 'browsed'
    db = get_db()
    admin_service.ignore_hostname(db, hostname_to_ignore)
    return redirect(url_for(origin), 303)

def get_db():
    if 'db' not in g:
        g.db = database.Database(db_name)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
