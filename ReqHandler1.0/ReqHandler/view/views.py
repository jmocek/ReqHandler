from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from ReqHandler import app, db, login_manager
from ReqHandler.form import RequirementAddForm, LoginForm, SignupForm
from ReqHandler.module_file.module_db_operations import DataBaseInputGenerator
from ReqHandler.module_file.models import User, Requirement
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.sql.expression import func
from sqlalchemy import desc


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = RequirementAddForm()

    if form.validate_on_submit():
        text = form.text.data
        product_version = form.product_version.data
        dbinput = DataBaseInputGenerator(version=None,
                                         text=text,
                                         product_version=product_version,
                                         baseline=None,
                                         links=None,
                                         author=current_user)
        dbinput.add_req()
        flash("Stored '{}'".format(text))
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/req')
def req():

    reqs = []
    # Pass only latest versions
    all_reqs = Requirement.query.all()
    # Get all nids
    nid_list = []
    for re in all_reqs:
        nid_list.append(re.nid)
    nid_list = set(nid_list)
    for nid in nid_list:
        # Get highest req version
        version = db.session.query(func.max(Requirement.version)).filter_by(nid=nid)
        requirement = Requirement.query.filter_by(nid=nid).filter_by(version=version).first()
        reqs.append(requirement)
    return render_template('req.html', reqs=reqs)


@app.route('/edit')
def edit():
    return render_template('edit.html')


@app.route('/find')
def find():
    return render_template('find.html')


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Logged in successfully as {}.".format(user.username))
            return redirect(request.args.get('next') or url_for('user', username=user.username))
        flash('Incorrect username or password.')
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, {}! Please login.'.format(user.username))
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)