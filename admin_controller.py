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

@app.route("/browsed")
def get_admin_page():
    return admin_service.render_admin_page(get_db())

@app.route("/block_hostname", methods = ["POST"])
def block_hostname():
    hostname_to_block = request.form['hostname']
    db = get_db()
    admin_service.block_hostname(db, hostname_to_block)
    return redirect(url_for('get_admin_page'), 303)

@app.route("/ignore_hostname", methods= ["POST"])
def ignore_hostname():
    hostname_to_ignore = request.form['hostname']
    db = get_db()
    admin_service.ignore_hostname(db, hostname_to_ignore)
    return redirect(url_for('get_admin_page'), 303)

def get_db():
    if 'db' not in g:
        g.db = database.Database(db_name)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
