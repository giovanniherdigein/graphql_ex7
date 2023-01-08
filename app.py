#! /usr/bin/python

from flask import Flask, request
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from bp_main import main as main_blueprint
from bp_auth import auth as auth_blueprint
from bp_admin import admin as admin_blueprint
from bp_scripts import scripts as scripts_blueprint
from config import db, bcrypt
from os import getenv
import os
from models import User
from datetime import timedelta
from flask_mail import Mail

# loading environment variables from here
load_dotenv()
app = Flask(__name__)  # entering the Flask application framework
# Login mananger with helpers for auth management
login_manager = LoginManager()
basedir = os.path.abspath(os.path.dirname(
    __file__))  # the location of this file
# joining the directory this file is in to locate the database instance
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////" + \
    os.path.join(
        basedir, 'database.sqlite')
# closing the interaction with the database on teardown
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# secret key settings
app.config['SECRET_KEY'] = getenv("SECRET_KEY")
# COOKIE SETTINGS
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=360)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=360)
# Here we'll make a few configurations for mail
app.config['MAIL_SERVER'] = getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = getenv('MAIL_PORT')
app.config['MAIL_USERNAME'] = getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# Some config for file handeling
app.config['UPLOAD_FOLDER'] = '/static/uploads/images/'
app.config['MAX_CONTENT_PATH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', 'svg', 'bmp']
# initializing the database with the app in context
db.init_app(app)
# bcrypt to hash our passwords using sha256 method
bcrypt.init_app(app)
# the login manager that will take care of authentication and authorization
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
# doing the same with the migration module
migrate = Migrate(app, db)
mail = Mail(app)
# registering the route blueprints
app.register_blueprint(main_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
# We can use this by calling the bp_name first like 'flask scripts bootstrap'
app.register_blueprint(scripts_blueprint)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


# registering the app on the wsgi server and getting it ready to run
if __name__ == "__main__":
    app.run()
