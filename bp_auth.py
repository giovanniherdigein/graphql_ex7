from flask import (Blueprint, render_template, redirect, url_for, request)
from flask_login import login_user, login_required, logout_user, current_user
from schema import schema
from models import User

auth = Blueprint('auth', __name__)

# auth ruotes are called using auth namespace 'auth.route'
login_query = '''
mutation loginUser($email:String!,$password:String!){
    loginUser(email:$email,password:$password){
        ok
        user{
            id
            email
        }
    }   
}
'''
register_query = '''
mutation registerUser($username:String!,$email:String!,$pw1:String!,$pw2:String!,$role:String!){
    registerUser(username:$username,email:$email,password1:$pw1,password2:$pw2,role:$role){
        ok
        user{
        id
        email
        }
        message
    }
}
'''


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get('password')
        result = schema.execute(request_string=login_query, variable_values={
            'email': email,
            'password': password
        }, auto_camelcase=False)

        if result.errors:
            print(result.errors)
        elif result.data['loginUser']['ok']:
            user = result.data['loginUser']['user']
        return redirect(url_for('main.profile'))
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')
        result = schema.execute(request_string=register_query, variable_values={
            'username': username,
            'email': email,
            'pw1': pw1,
            'pw2': pw2,
            'role': 'user'
        })
        if result.errors:
            data = result.errors
        else:
            data = result.data['registerUser']['user']

        return redirect(url_for('main.welcome', data=data))
    return render_template("register.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


upload_query = '''
    mutation uploadPicture($file:Upload!){
        uploadPicture(file:$file){
            ok
            filename
        }
    }
'''
create_query = '''
mutation ($firstname:String!,$lastname:String!,$picture:String!){
  addProfile(firstName:$firstname,lastName:$lastname,pictureUrl:$picture){
    ok
    profile{
      userid
      firstName
    }
  }
}
'''


@auth.route('/createprofile', methods=['GET', 'POST'])
@login_required
def create_profile():
    if request.method == 'POST':
        upl_result = schema.execute(
            upload_query, variable_values={'file': request.files['file']}, root_value=current_user)
        filename = upl_result.data['uploadPicture']['filename']
        create_result = schema.execute(
            create_query, variable_values={
                'firstname': request.form['firstname'],
                'lastname': request.form['lastname'],
                'picture': filename,
            }, root_value=current_user)
        outcome = create_result
        if outcome.errors:
            print(outcome.errors)
        else:
            print(outcome.data['addProfile']['ok'])
    return render_template('create_profile.html')
