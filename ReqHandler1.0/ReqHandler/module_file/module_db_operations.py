from ReqHandler import db
from sqlalchemy.sql.expression import func
from ReqHandler.module_file.models import Requirement, User


class DataBaseInputGenerator:

    def __init__(self, nid, version, text, product_version, baseline, links, author):
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
                                  links=self._links)

        db.session.add(requirement)
        db.session.commit()

    # def add_req_to_hist(self, req):
    #     """
    #     Method translates passed requirement to history-DB format and passes it to file handler.
    #     :param req: DB input dictionary.
    #     :return: updated Hist dictionary for test purposes
    #     """
    #     # Change key name to history format
    #     req_dict = self.translate_db_input_to_req_dict(req)
    #     hist_req = self.translate_req_dict_to_db_input(req_dict, 0)
    #     # Updated history db file
    #     self.historyDB.append_to_file(hist_req)
    #     self.Hist.update(hist_req)
    #     return self.Hist
    #
    # def update_req(self, nid, new_text, author):
    #     """
    #     Method handles existing requirement update. Old version is moved to hist-DB, new TIMESTAMP is generated.
    #     :param nid: nid of requirement to be updated
    #     :param new_text: new text version
    #     :param author: author of update
    #     :return: updated Req dictionary and new TIMESTAMP for test purposes.
    #     """
    #
    #     try:
    #         new_version = self.translate_db_input_to_req_dict({nid: self.Req[nid]})
    #
    #     except KeyError as name:
    #         print("No requirement with given nid", name)
    #         raise
    #         return
    #
    #     new_version["version"] = int(new_version["version"]) + 1
    #     new_version["text"] = new_text
    #     new_version["author"] = author
    #     new_version["time"] = self.get_time()
    #     new_version_db = self.translate_req_dict_to_db_input(new_version)
    #     # Remove old version from DB
    #     self.DB.remove_req_with_given_nid([nid])
    #     # Append new version
    #     self.DB.append_to_file(new_version_db)
    #     # Add old version to history db
    #     self.add_req_to_hist({nid: self.Req[nid]})
    #     # Return updated req dictionary
    #     self.Req.update(new_version_db)
    #     return self.Req, new_version["time"]
    #
    # def remove_req(self, nid_list):
    #     """
    #     Method removes passed requirements from requirement DB and move them to hist DB.
    #     :param nid_list: list of requirements nids to be removed
    #     :return: updated Req dictionary for test purposes.
    #     """
    #
    #     for nid in nid_list:
    #         self.add_req_to_hist({nid: self.Req[nid]})
    #
    #     self.DB.remove_req_with_given_nid(nid_list)
    #     self.Req = self.DB.load_db()
    #     return self.Req
    #
    # def find_req(self, nid_list):
    #     """
    #     Method searches for given requirement nids in requirement DB.
    #     :param nid_list: list of requirements nids
    #     :return: Found dictionary including found requirements in req. DB format, not_found dictionary for not found req
    #     uirements.
    #     """
    #     find_result = self.DB.find_req_with_nid(nid_list)
    #     not_found = {}
    #     not_found_nids = []
    #     for nid, value in find_result.items():
    #         if value == "Requirement not found":
    #             not_found.update({nid: value})
    #             not_found_nids.append(nid)
    #     for nid in not_found_nids:
    #         del find_result[nid]
    #
    #     return find_result, not_found
    #
    # def find_req_in_history(self, nid_list):
    #     """
    #     Method searches for given requirement nids in history DB.
    #     :param nid_list: list of requirements nids
    #     :return: Found dictionary including found requirements in req. DB format, not_found dictionary for not found req
    #     uirements.
    #     """
    #
    #     not_found = {}
    #     found_nids = []
    #     not_found_nids = []
    #     for nid in nid_list:
    #         versions = self.get_all_versions(nid)
    #         if not versions:
    #             not_found_nids.append(nid)
    #         else:
    #             for version in versions:
    #                 nid_v = str(nid) + "_" + str(version)
    #                 found_nids.append(nid_v)
    #     find_result = self.historyDB.find_req_with_nid(found_nids, 1)
    #
    #     for nid in not_found_nids:
    #         not_found.update({nid: "requirement does not have any history"})
    #
    #     return find_result, not_found
    #
    # def show_req(self, nid, db=1):
    #     """
    #     Method prints requirement data in std output.
    #     :param nid: nid of req, nid_v if history
    #     :return: string "Status ok" if no errors found.
    #     """
    #     if db:
    #         database = self.Req
    #     else:
    #         database = self.Hist
    #     try:
    #         req_instance = self.translate_db_input_to_req_dict({nid: database[nid]})
    #     except KeyError as name:
    #         print("No requirement with given nid", name)
    #         raise
    #
    #     print("Requirement ID: ", req_instance["nid"])
    #     print("Version: ", req_instance["version"])
    #     print("Text: ", req_instance["text"])
    #     print("Author: ", req_instance["author"])
    #     print("Product: ", req_instance["product"])
    #     print("Baseline: ", req_instance["baseline"])
    #     print("Created: ", self.show_time(req_instance["time"]))
    #     print("Links: ", req_instance["links"])
    #
    #     return "Status ok"
    #
    # def show_history(self, nid):
    #     """
    #     Method prints requirement current version data as well as all previous versions in std output.
    #     :param nid: nid of req
    #     :return: string "Status ok" if no errors found.
    #     """
    #     versions = self.get_all_versions(nid)
    #     self.show_req(nid)
    #     for version in versions:
    #         if version > 0:
    #             nid_v = str(nid) + "_" + str(version)
    #             self.show_req(nid_v, 0)
    #     return "Status ok"
    #
    # def clear_db(self, db=1):
    #     """
    #     Method clears DB- removes all requirement.
    #     Note! DB is noted moved to history!
    #     :param db: 1 for requirement and 0 for history db
    #     :return: Reg or Hist dictionary for test purposes
    #     """
    #     if db:
    #         self.DB.clear_database()
    #         self.Req = self.DB.load_db()
    #         return self.Req
    #     else:
    #         self.historyDB.clear_database()
    #         self.Hist = self.historyDB.load_db()
    #         return self.Hist
    #
    # def get_all_versions(self, nid):
    #     """
    #     Method returns all historical requirement version numbers.
    #     :param nid: requirement nid.
    #     :return: Returns all historical requirement version numbers
    #     """
    #     versions = []
    #     nid_v = str(nid) + "_1"
    #     v = 1
    #     while nid_v in self.Hist:
    #         versions.append(v)
    #         v += 1
    #         nid_v = str(nid) + "_" + str(v)
    #
    #     versions.sort(reverse=True)
    #     return versions
    #
    # @staticmethod
    # def translate_req_dict_to_db_input(req, db=1):
    #     """
    #     Static method translates dictionary which consist of requirement elements to readable/ready to save in
    #     DB dictionary.
    #     :param req:
    #     :param db: 1 for requirement and 0 for history db
    #     :return: req in format {nid: "csv data"}
    #     """
    #     if db:
    #         db_key = req["nid"]
    #     else:
    #         db_key = str(req["nid"]) + "_" + str(req["version"])
    #     db_list = ""
    #     db_list += str(req["nid"]) + ","
    #     db_list += str(req["version"]) + ","
    #     db_list += str(req["text"]) + ","
    #     db_list += str(req["author"]) + ","
    #     db_list += str(req["product"]) + ","
    #     db_list += str(req["baseline"]) + ","
    #     db_list += str(req["time"]) + ","
    #     db_list += str(req["links"])
    #
    #     req_db = {db_key: db_list}
    #     return req_db
    #
    # @staticmethod
    # def get_time():
    #     """
    #     Method returns current time in epoch float
    #     :return: float time()
    #     """
    #
    #     return time()
    #
    # @staticmethod
    # def show_time(time_float):
    #     """
    #     Returns printable view of time.
    #     :return: printable string
    #     """
    #     printable_time = strftime("%d %b %Y %H:%M:%S", gmtime(time_float))
    #     return printable_time
    #
    # @staticmethod
    # def translate_db_input_to_req_dict(req_db):
    #     """
    #     Translates db input into dictionary which consist of requirement elements.
    #     :param req_db:
    #     :return:
    #     """
    #     params = list(req_db.values())
    #     params = params[0].split(',')
    #     req_dict = {"nid": int(params[0])}
    #     req_dict.update({"version": int(params[1])})
    #     req_dict.update({"text": str(params[2])})
    #     req_dict.update({"author": str(params[3])})
    #     req_dict.update({"product": float(params[4])})
    #     req_dict.update({"baseline": int(params[5])})
    #     req_dict.update({"time": float(params[6])})
    #     req_dict.update({"links": str(params[7])})
    #
    #     return req_dict