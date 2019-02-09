#! /usr/bin/env python

from ReqHandler import app, db
from ReqHandler.module_file.models import User, Product
from flask_script import Manager, prompt_bool

manager = Manager(app)


@manager.command
def initdb():
    db.create_all()
    # db.session.add(User(username="mocek", email="ddd@upa.pl", password="test"))
    # db.session.add(User(username="arjen", email="arjen@example.com", password="test"))
    # db.session.add(Product(author="mocek", version="0.1"))
    # db.session.add(Product(author="mocek", version="0.2"))
    db.session.commit()
    print('Initialized the database')


@manager.command
def dropdb():
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        print('Dropped the database')


if __name__ == '__main__':
    manager.run()
