import os


class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = 'MY_SECRET_KEY'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + f'{BASE_DIR}/opinions_app/db.sqlite3'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
