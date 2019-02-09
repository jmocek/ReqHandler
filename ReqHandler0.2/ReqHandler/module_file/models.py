from datetime import datetime
from ReqHandler import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

association_table = db.Table('association',
                             db.Column('Requirement_id', db.Integer, db.ForeignKey('requirement.id')),
                             db.Column('ProductVersion_version', db.Float, db.ForeignKey('product.version')))

baseline_table = db.Table('baseline_association',
                          db.Column('Baseline_id', db.Integer, db.ForeignKey('baseline.id')),
                          db.Column('Requirement_id', db.Float, db.ForeignKey('requirement.id')))


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nid = db.Column(db.Integer)
    version = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    author = db.Column(db.String, db.ForeignKey('user.username'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    is_removed = db.Column(db.Boolean, default=False)
    product_version = db.relationship('Product', secondary=association_table,
                                      backref=db.backref('product_version', lazy='dynamic'))
    baseline = db.Column(db.String)
    links = db.Column(db.String)

    def __repr__(self):
        return "Requirement id: {} , version {}".format(self.nid, self.version)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    requirements = db.relationship('Requirement', backref='user', lazy='dynamic')
    product_versions = db.relationship('Product', backref='user', lazy='dynamic')
    baselines = db.relationship('Baseline', backref='user', lazy='dynamic')
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


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, db.ForeignKey('user.username'))
    version = db.Column(db.Float, unique=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get_versions():
        versions_list = []
        for v in Product.query.all():
            versions_list.append(v.version)
        return versions_list

    def __repr__(self):
        return "v{}".format(self.version)


class Baseline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, db.ForeignKey('user.username'))
    description = db.Column(db.String(1000))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    requirements = db.relationship('Requirement', secondary=baseline_table,
                                   backref=db.backref('requirements', lazy='dynamic'))

    def __repr__(self):
        return "Baseline id:{}, created:{}".format(self.id, self.time)
