from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from .config import PROD_DB, DEV_DB

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if os.environ.get('DEBUG') == '1':
    app.config['SQLALCHEMY_DATABASE_URI'] = DEV_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = PROD_DB

db = SQLAlchemy(app)


from . import routes
