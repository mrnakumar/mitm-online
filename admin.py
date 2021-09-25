import os

from flask import Flask
from flask import g
from flask import render_template
import database

app = Flask(__name__)

db_name = os.environ.get("db_name") or ":memory:"

@app.route("/admin")
def get_admin_page():
    hostnames = get_db().read_browsed()
    hostnames_sorted = sorted(hostnames)
    return render_template('admin.html', hostnames = hostnames_sorted)

def get_db():
    if 'db' not in g:
        g.db = database.Database(db_name)
        return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
