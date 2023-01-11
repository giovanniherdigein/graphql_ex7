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



