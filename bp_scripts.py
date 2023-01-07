from DictObj import DictObj
import click
from flask import Flask
from schema import schema
from flask import Blueprint

# ik maak deze blueprint om commandline scripts te kunnen uitvoeren in app.app_context
# ik heb hiermee toegang tot de wsgi server en kan met alle opties werken bijv. request, g, blueprints etc.etc
scripts = Blueprint('scripts', __name__)


@scripts.cli.command('initdb')
def initdb():
    '''Drops all tables and recreates the database from the given models'''
    db.drop_all()
    db.create_all()


@scripts.cli.command('bootstrap')
def bootstrap():
    '''
    Creates tables and iserts some data in them using grpaql schema architecture
    '''
    from models import (User, Role)
    from flask import jsonify
    db.drop_all()
    db.create_all()
    # fill the database with information
    super_user = Role('superuser')
    admin = Role("admin")
    user = Role('user')
    db.session.add(admin)
    db.session.add(user)
    db.session.add(super_user)

# Met deze algoritme heb ik heel handig gebruik gemaakt van de Dictionary
# ik kan nu ee dictionary aanbieden  aan de query
# en de dictionary die ik ontvang weer omzetten zodat ik weer een object het om mee te werken
# ik ben benieuwd hoe dat werkt als ik straks met formuliern werk

    users = [  # een list van dicts
        {
            'username': 'jan',
            'email': 'jan@example.org',
            'pw1': 'jan1234',
            'pw2': 'jan1234',
            'role': ''

        },
        {
            'username': 'andre',
            'email': 'andre@example.org',
            'pw1': 'andre123',
            'pw2': 'jan1234',
            'role': ''
        },
        {
            'username': 'koen',
            'email': 'koen@example.org',
            'pw1': 'koen123',
            'pw2': 'jan1234',
            'role': ''
        },
        {
            'username': 'beth',
            'email': 'beth@example.org',
            'pw1': 'beth123',
            'pw2': 'jan1234',
            'role': ''
        }
    ]
    print("Creating users: .....")
    for user in users:
        # db.session.add(u)
        # print(u)
        query_string = """
            mutation registerUser($username:String,$email:String,$password1:String,$password2:String){
                registerUser(username: $username, email:$email , password1: $password1, password2:$password2) {
                    ok
                    user {
                    username
                    email
                    password
                    }
                }
            }
        """
# hier doe ik de conversie naar object
        u = DictObj(user)
        variable_values = {
            "username": u.username,
            "email": u.email,
            "password1": u.pw1,
            "password2": u.pw2,
            "role": u.role
        }
        result = schema.execute(query_string, variable_values=variable_values)
        #data = result['data']['registerUser']
        #obj = DictObj(data)
        # print(jsonify(obj))
    # db.session.commit()
        data = result.data
# en hier volgt de conversie terug naar object
        obj = DictObj(data['registerUser'])
        if obj.ok:
            print(
                f"\r\nusername: {obj.user.username}  \r\nemail: {obj.user.email} \r\npassword: {obj.user.password}")

# ik kan hiermee click argumenten uit proberen. Die door tegeven aan de script
# tevens probeer ik ook mutatie algoritme uit gemaakt met schema queries aan de API


@scripts.cli.command('add_user')
@click.argument('username')
@click.argument('email')
@click.argument('pw1')
@click.argument('pw2')
@click.argument('role')
def add_user(username, email, pw1, pw2, role):
    '''
    args: username, email, pw1, pw2
    \r\nRegisters a user to the database
    '''
    query_string = """
        mutation registerUser($username:String,$email:String,$password1:String,$password2:String,$role:String){
            registerUser(username: $username, email:$email , password1: $password1, password2:$password2,role:$role) {
                ok
                user {
                username
                email
                password
                role
                }
            }
        }
    """
# variable values om extern argumenten door tegen aan de query
    variable_values = {
        "username": username,
        "email": email,
        "password1": pw1,
        "password2": pw2,
        "role": role
    }
    result = schema.execute(query_string, variable_values=variable_values)
    data = result['data']['registerUser']
    obj = DictObj(data)
    print(obj)


# zoeken en ophalen van een record uit de database
# middels click arguments
@scripts.cli.command('query_user')
@click.argument('username')
def query_user(username):
    '''
    args: username
    \r\nQueries a user from the User table
    '''
    from models import User
    user = User.query.filter_by(username=username).first()
    print("Naam: %s, Email: %s\r\nPassword: %s" %
          (user.username, user.email, user.password))
