import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = 'MY_SECRET_KEY'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + f'{BASE_DIR}/opinions_app/db.sqlite3'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+f'{BASE_DIR}\\'+os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')


# create.env file with data:
# FLASK_APP=opinions_app
# FLASK_ENV=development
# FLASK_DEBUG=1
# DATABASE_URI=opinions_app\\db.sqlite3
# SECRET_KEY=YOUR_SECRET_KEY
