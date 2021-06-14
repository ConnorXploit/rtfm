# encoding: utf-8
from .rtfm import app, json, os
from flask import g
import os, sqlite3

DIR_ACTUAL = os.path.dirname(os.path.realpath(__file__))

global_conf = {}
with open( os.path.join(DIR_ACTUAL, 'config.json') , 'r') as f:
    global_conf = json.loads( f.read() )

frases = global_conf['INDEX']['FRASES']

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rtfm.db'),
    SECRET_KEY=r'HF93YqzrJFHA}2uBsw3k\p?fFj>m$?$SZBwL"r=84VSE+q1R/"ea$BXsaXHE%Sh'
))
app.config.from_envvar('RTFM_SETTINGS', silent=True)
app.config['UPLOAD_PATH'] = os.path.join(DIR_ACTUAL, global_conf['INDEX']['UPLOAD_PATH'])
app.config['DOWNLOAD_PATH'] = os.path.join(DIR_ACTUAL, global_conf['INDEX']['DOWNLOAD_PATH'])

send_if_less = global_conf['INDEX']['SEND_IF_LESS']

if not os.path.isdir(app.config['UPLOAD_PATH']):
    os.mkdir( app.config['UPLOAD_PATH'] )

if not os.path.isdir(app.config['DOWNLOAD_PATH']):
    os.mkdir( app.config['DOWNLOAD_PATH'] )

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')