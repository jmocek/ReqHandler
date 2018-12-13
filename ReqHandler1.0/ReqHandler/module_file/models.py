from datetime import datetime
from ReqHandler import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nid = db.Column(db.Integer)
    version = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    author = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    product_version = db.Column(db.Float)
    baseline = db.Column(db.String)
    links = db.Column(db.String)

    def __repr__(self):
        return "Requirement id: {} , version {}".format(self.nid, self.version)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    requirements = db.relationship('Requirement', backref='user', lazy='dynamic')
    password_hash = db.Column(db.String)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)

