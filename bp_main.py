from flask_graphql import GraphQLView
from flask import (Blueprint, render_template, request)
from schema import schema
from flask_login import current_user, login_required
from flask_mail import Mail, Message

main = Blueprint("main", __name__)
main.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

mail = Mail()


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():

    return render_template('profile.html')


@main.route('/sendmail')
@login_required
def send_mail():
    msg = Message('Hello from the other side!',
                  sender='<<info@example.org>>', recipients=['podakek531@cnxcoin.com'])
    msg.body = "Hey Paul, This is another email to test and see ."
    mail.send(msg)

    return render_template('mail_return.html', message="Message sent succesfull")


@main.route('/welcome')
def welcome():
    data = request.args
    return render_template('welcome.html', data=data)
