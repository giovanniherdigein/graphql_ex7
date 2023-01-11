from graphene import (String, relay, ObjectType, Context,
                      Schema, Mutation, Boolean, Field, Int, ID, InputObjectType, InputField, Argument)
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import (User, Role, Profile, Post, Comments)
from werkzeug.security import generate_password_hash, check_password_hash
from config import db, bcrypt
from flask import request
from flask_login import login_user
from graphene_file_upload.scalars import Upload


class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User
        interfaces = (relay.Node,)


class RoleType(SQLAlchemyObjectType):
    class Meta:
        model = Role
        interfaces = (relay.Node,)


class ProfileType(SQLAlchemyObjectType):
    class Meta:
        model = Profile
        interfaces = (relay.Node,)


class Query(ObjectType):
    all_users = SQLAlchemyConnectionField(UserType)
    all_roles = SQLAlchemyConnectionField(RoleType)
    get_role_by_id = Field(lambda: RoleType, id=ID())
    get_user_by_id = Field(lambda: UserType, id=ID())

    def resolve_get_role_by_id(root, info, id):
        '''Getting a role by id'''
        return Role.query.get(id)

    def resolve_get_user_by_id(root, info, id):
        '''Getting a user by id'''
        return User.query.get(id)


class AddRole(Mutation):
    class Arguments:
        title = String()

    'Fields'
    ok = Boolean()
    role = Field(RoleType)
    message = String()

    def mutate(parent, info, title):
        role = Role(title)
        db.session.add(role)
        db.session.commit()
        ok = True
        message = "geslaagd"
        role = role

        return AddRole(ok=ok, role=role, message=message)


class Remove(Mutation):
    class Arguments:
        id = ID()

    'Fields'
    ok = Boolean()
    user = Field(UserType)
    message = String()

    def mutate(parent, info, id):
        user = User.query.get(id)
        db.session.delete(user)
        # db.commit()
        ok = True
        user = user
        message = 'Deleted'

        return Remove(ok=ok, message=message, user=user)


class Register(Mutation):
    class Arguments:
        username = String()
        email = String()
        password1 = String()
        password2 = String()
        role = String()

    'Fields'
    ok = Boolean()
    message = String()
    user = Field(UserType)

    def mutate(parent, info, username, email, password1, password2, role='user'):
        if not password1 == password2:
            ok = False
            message = "Er ging iets mis"
            user = None
            # return Register(ok=ok, user=user, message=message)
        else:
            pw_hash = generate_hash(password1)
            userRole = Role.query.filter_by(title=role).first()
            user = User(username, email, pw_hash, userRole)
            db.session.add(user)
            db.session.commit()
            ok = True
            message = 'Geslaagd gebruiker aangemaakt'
            # return Register(ok=ok, user=user, message=message)
        return Register(ok=ok, user=user, message=message)


class Login(Mutation):
    class Arguments:
        email = String(required=True)
        password = String(required=True)

    'Fields'
    user = Field(UserType)
    ok = Boolean()
    message = String()
    id = Int()

    def mutate(parent, info, email=None, password=None):
        if not email == None:
            user = User.query.filter_by(email=email).first()
        if check_hash(user.password, password):
            login_user(user, remember=True)
            ok = True
            message = 'OK'
            id = user.id
            return Login(ok=ok, message=message, user=user, id=id)


def generate_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def check_hash(pw_hash, password):
    return bcrypt.check_password_hash(pw_hash, password)


class AddProfile(Mutation):
    class Arguments:
        userid = Int()
        first_name = String()
        last_name = String()
        picture_url = String()

    'Fields'
    ok = Boolean()
    profile = Field(lambda: ProfileType)

    def mutate(root, info, first_name, last_name, picture_url):
        # if I use it onlt i should use this --> info.context.args.get('userid')
        uid = root.id
        profile = Profile(uid, first_name, last_name, picture_url)
        db.session.add(profile)
        db.session.commit()
        ok = True

        return AddProfile(ok=ok, profile=profile)


class EditProfile(Mutation):
    class Arguments:
        userid = Int()
        first_name = String()
        last_name = String()
        picture_url = String()

    'Fields'
    ok = Boolean()

    def mutate(root, info, first_name=None, last_name=None, picture_url=None):
        # if I use it onlt i should use this --> info.context.args.get('userid')
        # uid = root.id
        # profile = Profile.query.filter_by(uid=uid).first()
        # if not profile == None:
        if not first_name == None and not first_name == root.profile.first_name:
            root.profile.first_name = first_name
        if not last_name == None and not last_name == root.profile.last_name:
            root.profile.last_name = last_name
        if not picture_url == None and not picture_url == root.profile.picture:
            root.profile.picture = picture_url

        db.session.commit()
        ok = True

        return EditProfile(ok=ok)


class Update(Mutation):
    class Arguments:
        id = ID(required=True)
        username = String()
        email = String()
        password = String()
        role = String()

    ' Fields '
    ok = Boolean()
    user = Field(UserType)

    def mutate(parent, info, id, username=None, email=None, password=None, role=None):
        user = User.query.get(id)
        if not username == None and username != user.username:
            user.username = username
        if not email == None and email != user.email:
            user.email = email
        if not password == None and check_hash(user.password, password):
            user.password = password
        if Role.query.filter_by(title=role).first() != user.role and not role == None:
            user.role = Role.query.filter_by(title=role).first()
        return Update(ok=True, user=user)


class UploadPicture(Mutation):

    class Arguments:
        file = Upload(required=True)
        # pass

    ' Fields '
    ok = Boolean()
    filename = String()
    # @classmethod

    def mutate(root, info, file, **kwargs):
        import os
        os.makedirs(os.path.join('static/uploads',
                    str(root.id)), exist_ok=True)
        file.save(os.path.join('static/uploads', str(root.id), file.filename))
        # print("File saved %" % file)
        return UploadPicture(ok=True, filename=file.filename)


class ChangePassword(Mutation):
    """Changes the user password """
    class Arguments:
        password = String()

    'Fields'
    ok = Boolean()
    user = Field(lambda: UserType)

    def mutate(root, info, password, **kwargs):
        _id = info.context.args.get('userid')
        user = User.query.get(int(_id))
        if not check_hash(user.password, password):
            user.password = password
            db.session.commit()
            ok = True
        return ChangePassword(ok=ok, user=user)


class Mutation(ObjectType):
    add_profile = AddProfile.Field(description="Adds a profile to a user")
    edit_profile = EditProfile.Field(description="Edits the profile ")
    upload_picture = UploadPicture.Field(
        description="Uploads a file to the system")
    login_user = Login.Field()
    register_user = Register.Field(
        description="Registers a user to the system")
    delete_user = Remove.Field()
    update_user = Update.Field()
    add_role = AddRole.Field(description="Adds a role to the system")


schema = Schema(query=Query, mutation=Mutation)
