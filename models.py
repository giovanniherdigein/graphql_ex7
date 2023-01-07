from config import db
from datetime import datetime
from flask_login import UserMixin


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    # users = db.relationship("User", backref='role')

    def __init__(self, title):
        self.title = title


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    roleid = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users', uselist=False)
    profile = db.relationship('Profile', backref='user', uselist=False)
    is_active = db.Column(db.Boolean(), default=True)
    is_authenticated = db.Column(db.Boolean(), default=True)
    is_anonumous = db.Column(db.Boolean(), default=True)

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    # @classmethodexit()
    def add_profile(self, fname, lname, picUrl):
        profile = Profile(self.id, fname, lname, picUrl)
        db.session.add(profile)
        db.session.commit()
        return profile

    # @classmethod
    def get_profile(self):
        profile = Profile.query.filter_by(userid=self.id).last()
        return profile

    def get_id(self):
        return str(self.id)


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.ForeignKey(User.id))
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    picture = db.Column(db.String())
    last_updated = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, uid, fname, lname, picUrl):
        self.userid = uid
        self.first_name = fname
        self.last_name = lname
        self.picture = picUrl

    def __repr__(self):
        return f"<Profile of {self.first_name}>"
