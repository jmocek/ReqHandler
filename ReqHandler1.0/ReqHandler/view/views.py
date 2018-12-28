from flask import render_template, request, flash, redirect, url_for, send_from_directory
from ReqHandler import login_manager
from ReqHandler.view.form import RequirementAddForm, LoginForm, SignupForm, ExportForm
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from ReqHandler.view.view_support import *
import os


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
        dbinput = DataBaseInputGenerator(nid=None,
                                         version=None,
                                         text=text,
                                         product_version=product_version,
                                         baseline=None,
                                         links=None,
                                         author=current_user,
                                         is_removed=None)
        dbinput.add_req()
        flash("Stored '{}'".format(text))
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/req')
@login_required
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
        if requirement.is_removed is False:
            reqs.append(requirement)
    return render_template('req.html', reqs=reqs)


@app.route('/edit/<int:nid_id>', methods=['GET', 'POST'])
@login_required
def edit(nid_id):
    requirement = Requirement.query.get_or_404(nid_id)
    form = RequirementAddForm(obj=requirement)
    if form.validate_on_submit():
        form.populate_obj(requirement)
        text = form.text.data
        product_version = form.product_version.data
        nid = requirement.nid
        version = requirement.version + 1
        dbinput = DataBaseInputGenerator(nid=nid,
                                         version=version,
                                         text=text,
                                         product_version=product_version,
                                         baseline=None,
                                         links=None,
                                         author=current_user)
        dbinput.add_req()
        flash("Stored '{}'".format(text))
        return redirect(url_for('user', username=current_user.username))
    return render_template('edit.html', requirement=requirement, form=form)


@app.route('/remove/<int:nid_id>', methods=['GET', 'POST'])
@login_required
def remove_req(nid_id):
    # For macros compatiblity requirement shall be in a list object
    reqs = []
    requirement = Requirement.query.get_or_404(nid_id)
    reqs.append(requirement)
    if request.method == "POST":
        requirement.is_removed = True
        db.session.commit()
        flash("Removed requirement ID:'{}'".format(requirement.nid))
        return redirect(url_for('req'))
    else:
        flash("Please confirm removing the requirement.")
    return render_template('confirm_remove.html', requirement=reqs, nolinks=True)


@app.route('/user/<username>')
@login_required
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


@app.route('/export', methods=['GET', 'POST'])
@login_required
def export():
    form = ExportForm()

    if form.validate_on_submit():
        filename = form.filename.data
        export_file()
        uploads = os.path.join(app.root_path)

        return send_from_directory(directory=uploads, filename="db.csv", as_attachment=True,
                                   attachment_filename=filename)
    return render_template('export.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return render_template('upload.html')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Successfully imported file ', filename)
            return redirect(url_for('import_file',
                                    filename=filename))
    return render_template('upload.html')


@app.route('/import/<filename>', methods=['GET', 'POST'])
@login_required
def import_file(filename):
    if request.method == 'POST':
        if verify_file(filename):
            if import_from_file(filename):
                flash('File imported successfully')
                return redirect(url_for('req'))
        elif verify_file(filename) is False:
            flash('Incorrect file content')
            return redirect(url_for('req'))
        else:
            flash('Empty file!')
            return redirect(url_for('req'))

    return render_template('import.html')
