import os

from flask import Flask
from flask import g
from flask import render_template
import database

app = Flask(__name__)

db_name = os.environ.get("db_name") or ":memory:"

@app.route("/admin")
def hello_world():
    return render_template('admin.html')

def get_db():
    if 'db' not in g:
        g.db = database.Database(db_name)
        return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
