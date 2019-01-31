from dateutil import parser
import datetime
from flask_login import current_user
from ReqHandler import db, app, ALLOWED_EXTENSIONS
import csv
from sqlalchemy.sql.expression import func
from ReqHandler.module_file.models import Requirement, User, Product
import os
from ReqHandler.view.form import RequirementAddForm, BaselineForm
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField, SelectField


class DataBaseInputGenerator:

    def __init__(self, nid, version, text, product_versions, baseline, links, author, is_removed):
        if nid is None:
            nid = self.get_last_nid() + 1
        self._nid = nid
        if version is None:
            version = 1
        self._version = version
        self._text = text
        self._product_versions = product_versions
        if baseline is None:
            baseline = "undefined"
        self._baseline = baseline
        if links is None:
            links = "not+yet+implemented"
        self._links = links
        self._author = author
        if is_removed is None:
            is_removed = False
        self._is_removed = is_removed

    @staticmethod
    def get_last_nid():
        """
        Returns last used requirement nid if any, 0 if DB is empty.
        :return: last used nid OR 0
        """
        if db.session.query(func.max(Requirement.nid)).scalar():
            return db.session.query(func.max(Requirement.nid)).scalar()
        else:
            return 0

    def add_req(self):
        """
        Method generates requirement dictionary and passes it to module_file Class which handles it.
        :param req: Dictionary that consists of keys: version, txt, author, time, baseline, product and links.
        :return: updated Req dictionary and TIMESTAMP for test purposes.
        """

        requirement = Requirement(nid=self._nid,
                                  version=self._version,
                                  text=self._text,
                                  baseline=self._baseline,
                                  user=self._author,
                                  links=self._links,
                                  is_removed=self._is_removed)

        db.session.add(requirement)
        db.session.commit()
        for version in self._product_versions:
            print("THYS IS VERSION: ", version)
            pv = Product.query.filter_by(version=version).first()
            requirement.product_version.append(pv)
            db.session.commit()

    def check_edit(self):
        new_text = self._text
        new_products = self._product_versions
        print("new text, new products:", new_text, new_products)
        # here will land other comparisons
        version = self._version - 1
        old_requirement = Requirement.query.filter_by(nid=self._nid).filter_by(version=version).first()
        old_text = old_requirement.text
        old_products_v = old_requirement.product_version
        old_products = []
        for product in old_products_v:
            old_products.append(product.version)
        print("old text, old products:", old_text, old_products)

        if new_text == old_text and new_products == old_products:
            return False
        # elif new_text == old_text and new_products != old_products:
        #     return True
        # elif new_text != old_text and new_products == old_products:
        #     return True
        else:
            return True

def export_file():
    """

    :return:
    """

    path = os.path.join(app.root_path, "db.csv")
    with open(path, 'r+', newline='') as csvfile:
        csvfile.truncate(0)
        fieldnames = ['nid', 'version', 'text', 'author', 'product versions', 'baseline', 'time', 'links', 'isremoved']
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        requirements = db.session.query(Requirement).all()
        for req in requirements:
            print(req)
            product_versions = ""
            for pv in req.product_version:
                product_versions += str(pv.version) + "+"
            # truncate last separator
            product_versions = product_versions[:-1]
            writer.writerow({'nid': req.nid,
                             'version': req.version,
                             'text': req.text,
                             'author': req.author,
                             'product versions': product_versions,
                             'baseline': req.baseline,
                             'time': req.time,
                             'links': req.links,
                             'isremoved': req.is_removed})
    csvfile.close()


def remove_file(filename):
    """

    :param filename:
    :return:
    """
    path = os.path.join(app.root_path, filename)
    os.remove(path)


def get_params(filename):
    reqs = []
    path = os.path.join(app.root_path, filename)
    with open(path, 'r', newline='') as csvfile:
        # Skip header:
        is_empty = csvfile.readline()
        if len(is_empty) == 0:
            return 0
        for line in csvfile:
            pamlist = []
            print(line)
            param_list = line.split('"')
            if len(param_list) == 3:
                pamlist1 = param_list[0].split(',')[:-1]
                pamlist2 = param_list[1]
                pamlist3 = param_list[2].split(',')[1:]
                for pam in pamlist1:
                    pamlist.append(pam)
                pamlist.append(pamlist2)
                for pam in pamlist3:
                    pamlist.append(pam)
            else:
                pamlist = line.split(',')
            print(pamlist)
            reqs.append(pamlist)
    csvfile.close()
    return reqs


def verify_file(filename):

    reqs = get_params(filename)
    if reqs == 0:
        return 0
    for req in reqs:
        if len(req) != 9:
            print('Incorrect params', req[8][:-2], req[0], req[1], "len: ", len(req))
            return False

        try:
            int(req[0])
        except ValueError:
            print('NID is not an integer')
            return False

        try:
            int(req[1])
        except ValueError:
            print('Version is not an integer')
            return False

        if len(req[2]) > 1000:
            print('TEXT is too long')
            return False

        if len(req[3]) > 100:
            print('AUTHOR is too long')
            return False

        if len(req[4]) < 1:
            print('PRODUCT_VERSIONS not set')
            return False

        if req[5] != 'undefined':
            print('Unsupported BASELINE')
            return False

        if not isinstance(parser.parse(req[6]), datetime.datetime):
            print('Incorrect DATETIME')
            return False

        if req[7] != 'not+yet+implemented':
            print('Unsupported LINKS')
            return False

        isremoved = req[8][:-2]
        if isremoved != "True":
            if isremoved != "False":
                print('Unsupported IsRemoved', req[8][:-2], req[0], req[1])
                return False

    return True


def import_from_file(filename):

    reqs = get_params(filename)
    for req in reqs:
        if req[8][:-2] == "True":
            is_removed = True
        else:
            is_removed = False
        product_versions = req[4].split("+")
        dbinput = DataBaseInputGenerator(nid=None,
                                         version=None,
                                         text=req[2],
                                         baseline=None,
                                         links=None,
                                         product_versions=product_versions,
                                         author=current_user,
                                         is_removed=is_removed)
        dbinput.add_req()

    remove_file(filename)

    return True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_product_forms():
    class Add(RequirementAddForm):
        pass
    existing_products = []
    for product in Product.query.all():
        name = "v" + str(product.version)
        name = name.replace(".", "_")
        setattr(Add, name, BooleanField(str(product.version)))
        existing_products.append(name)

    return Add, existing_products


def create_baseline_forms():
    class Add(BaselineForm):
        pass

    versions = []
    for product in Product.query.all():
        version = (product.version, product)
        print(version)
        versions.append(version)

    print(versions)
    setattr(Add, "product_version", SelectField('Baseline product version', coerce=float, choices=versions))

    return Add


def amend_reqs(version, baseline):
    print("pv", version)
    pversion = Product.query.filter_by(version=version).first()
    print("pv", pversion)
    for req in Requirement.query.filter_by(is_removed=False)\
            .filter(Requirement.product_version.contains(pversion)).all():

        print(req)
        baseline.requirements.append(req)
        db.session.commit()
    print("reqi: ", baseline.requirements)

