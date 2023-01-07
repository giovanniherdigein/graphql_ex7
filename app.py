#! /usr/bin/python

from DictObj import DictObj
import click
from flask import Flask, request
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
from bp_main import main as main_blueprint
from bp_auth import auth as auth_blueprint
# from bp_scripts import scripts as scripts_blueprint
from config import db, bcrypt
import os
from os import getenv
from models import User
from schema import schema
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
app.config['REMEMBER_COOKIE_DURATION'] = 3600
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
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
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
# app.register_blueprint(scripts_blueprint)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


class TempUser(object):
    '''A TempUser as hepler to insert soome data in the database '''
    username = ""
    email = ""
    pw1 = ""
    pw2 = ""
    role = ""

    def __init__(self, username, email, pw1, pw2, role):
        self.username = username
        self.email = email
        self.pw1 = pw1
        self.pw2 = pw2
        self.role = role


@app.cli.command('bootstrap')
def bootstrap():
    from getpass import getpass
    import sys
    '''
    Creates tables and inserts some data in them using graphql schema architecture
    '''
    from models import (User, Role, Profile)
    db.drop_all()
    db.create_all()
    # fill the database with information
    # super_user = Role('superuser')
    # admin = Role("admin")
    # usr = Role('user')
    # db.session.add(admin)
    # db.session.add(usr)
    # db.session.add(super_user)
    # db.session.commit()
    # #####################
    # Let's try this to start using graphql as communication "ast" layer
    # to talk to our API

    roles = ["superuser", "admin", "user", "anonymous"]
    roles_query = """
    mutation addRole($title:String){
        addRole(title:$title){
            ok
            role{
            title
            }
        }
    }
    """
    print("We will add an adminstrator to the system first")
    print("please enter the email first")
    email = input("Email\n")
    print("Admin email is {%s}\n" % email)
    print("Now enter the password .....")
    password = getpass("Password ?\n")
    assert password == getpass("Password again please ?\n")

    for role in roles:
        roles_values = {"title": role}
        result = schema.execute(roles_query, variable_values=roles_values)
        data = result.data['addRole']
        if data['ok']:
            print(data['role']['title']+' Toegevoegd')

# Met deze algoritme heb ik heel handig gebruik gemaakt van de Dictionary
# ik kan nu ee dictionary aanbieden  aan de query
# en de dictionary die ik ontvang weer omzetten zodat ik weer een object het om mee te werken
# ik ben benieuwd hoe dat werkt als ik straks met formuliern werk
# een list van dicts

    # print('Ok'+data['user']['username']
    #       ) if data['ok'] else print('something went wrong, sorry')
    # print(data)
    pw_hash = bcrypt.generate_password_hash(password)
    adm_role = Role.query.filter_by(title='admin').first()
    admin = User("admin", email, pw_hash, adm_role)
    db.session.add(admin)
    db.session.commit()
    print("#########################")
    print("Admin added to the system")
    print("#########################")
    users = [
        TempUser(username="jan", email='jan@example.org',
                 pw1="jan123", pw2="jan123", role='user'),
        TempUser(username='andre', email='andre@example.org',
                 pw1='andre123', pw2='andre123', role='user'),
        TempUser(username='koen', email='koen@example.org',
                 pw1='koen123', pw2='koen123', role='user'),
        TempUser(username='beth', email='beth@example.org',
                 pw1='beth123', pw2='beth123', role='user'),
        TempUser(username='nina', email='nina@example.org',
                 pw1='nina123', pw2='nina123', role='user')
    ]
    create = input("\rShould we enter some dummy users (y/n)?\n")
    if create == 'n':
        return
    else:
        print("Creating users: .....")
        print("Please wait .........\n")
        for user in users:
            #         # db.session.add(u)
            #         # print(u)
            query_string = """
                mutation registerUser($username:String,$email:String,$password1:String,$password2:String,$role:String){
                    registerUser(username: $username, email:$email , password1: $password1, password2:$password2,role:$role){
                        ok
                        user {
                        username
                        email
                        password
                        role{
                            title
                        }
                        }
                        message
                    }
                }

            """
    # # hier doe ik de conversie naar object
            # u = DictObj(user)
            variable_values = {
                "username": user.username,
                "email": user.email,
                "password1": user.pw1,
                "password2": user.pw2,
                "role": user.role
            }
            result = schema.execute(
                query_string, variable_values=variable_values)
            # data = result
            # obj = DictObj(data)
            # print(jsonify(obj))
            # db.session.commit()
            data = result.data['registerUser']
    # en hier volgt de conversie terug naar object
            # obj = DictObj(data['registerUser'])
            # if obj.ok:
            #     print(
            #         f"\r\nid:{obj.user.id} \r\nusername: {obj.user.username}  \r\nemail: {obj.user.email} \r\npassword: {obj.user.password}\r\n Role Id:{obj.user.roleid}")
            #     print(obj.message)

            # else:
            #     print('\r\n'+obj.message)
    # zonder conversie is dat
            # obj = data['registerUser']
            # if obj['ok']:
            #     print(obj)
            print("\r"+data['user']['username']+" added succesfully !")
        print("\r\nFinished task!!\n")


@app.cli.command('updProfile')
def update_profile():
    '''The string to manupulate the users profile looks lik this'''
    query_string = '''
        mutation addProfile($userid:Int,$firstName:String,
        $lastName:String,$picture:String) {
            addProfile(userid:$userid,firstName: $firstName,
            lastName: $lastName, picture: $picture){
                ok
                profile {
                id
                userid
                firstName
                lastName
                lastUpdated
                user{
                    id
                    email
                    role{
                    title
                    }
                }
                }
            }
        }

    '''
    variable_values = set_variables("Nina", "Simone", "Simone.png")
    user_root = set_root(5)
    result = schema.execute(request_string=query_string,
                            variable_values=variable_values, root=user_root)
    data = result.data
    print(data)


def set_variables(fn, ln, pic):
    ''' Returns a dict containing the keys'''
    var_vals = {
        "firstName": fn,
        "lastName": ln,
        "picture": pic
    }
    return var_vals


def set_root(num):
    '''Returns the user we need to complete our script'''
    from models import User
    return User.query.filter_by(id=num).first()


# registering the app on the wsgi server and getting it ready to run
if __name__ == "__main__":
    app.run()
