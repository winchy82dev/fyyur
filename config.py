import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:pop@localhost:5432/fyyur2'
SQLALCHEMY_TRACK_MODIFICATIONS = True
WTF_CSRF_SECRET_KEY = '192b9bdd22ab9ed4d12e23'
SECRET_KEY = 'fcb9a393ec15f71bbf5dc9'
