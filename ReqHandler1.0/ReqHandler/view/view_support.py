from dateutil import parser
import datetime
from flask_login import current_user
from ReqHandler import db, app, ALLOWED_EXTENSIONS
import csv
from sqlalchemy.sql.expression import func
from ReqHandler.module_file.models import Requirement, User
import os


class DataBaseInputGenerator:

    def __init__(self, nid, version, text, product_version, baseline, links, author, is_removed):
        if nid is None:
            nid = self.get_last_nid() + 1
        self._nid = nid
        if version is None:
            version = 1
        self._version = version
        self._text = text
        self._product_version = product_version
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
                                  product_version=self._product_version,
                                  baseline=self._baseline,
                                  user=self._author,
                                  links=self._links,
                                  is_removed=self._is_removed)

        db.session.add(requirement)
        db.session.commit()


def export_file():
    """

    :return:
    """

    path = os.path.join(app.root_path)
    file = path + "\\db.csv"
    with open(file, 'r+', newline='') as csvfile:
        csvfile.truncate(0)
        fieldnames = ['nid', 'version', 'text', 'author', 'product', 'baseline', 'time', 'links', 'isremoved']
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        requirements = db.session.query(Requirement).all()
        for req in requirements:
            print(req)
            writer.writerow({'nid': req.nid,
                             'version': req.version,
                             'text': req.text,
                             'author': req.author,
                             'product': req.product_version,
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
    path = os.path.join(app.root_path)
    file = path + "\\" + filename
    os.remove(file)


def get_params(filename):
    reqs = []
    path = os.path.join(app.root_path)
    file = path + "\\" + filename
    with open(file, 'r', newline='') as csvfile:
        # Skip header:
        is_empty = csvfile.readline()
        if len(is_empty) == 0:
            return 0
        for line in csvfile:
            pamlist = []
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
            print('Incorrect params', req[8][:-2], req[0], req[1])
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

        try:
            float(req[4])
        except ValueError:
            print('PRODUCT_VERSION is not a double')
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

        dbinput = DataBaseInputGenerator(nid=None,
                                         version=None,
                                         text=req[2],
                                         product_version=req[4],
                                         baseline=None,
                                         links=None,
                                         author=current_user,
                                         is_removed=is_removed)
        dbinput.add_req()
    remove_file(filename)

    return True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
