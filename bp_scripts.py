from DictObj import DictObj
import click
from flask import Flask
from schema import schema
from flask import Blueprint

# ik maak deze blueprint om commandline scripts te kunnen uitvoeren in app.app_context
# ik heb hiermee toegang tot de wsgi server en kan met alle opties werken bijv. request, g, blueprints etc.etc
scripts = Blueprint('scripts', __name__)


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


@scripts.cli.command('bootstrap')
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


@scripts.cli.command('updProfile')
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
