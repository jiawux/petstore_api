import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False #unnecessary features disabled

"""
Using SQLite since it's a small application and doesn't require a server
Good practice setting up configuration from environment variable i.e. DATABASE_URL 
If url not availble then configure data base app.db from main directory

"""
