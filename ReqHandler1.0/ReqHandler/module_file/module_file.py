import csv
import os.path
from time import gmtime, strftime, time





class DataBaseOperations:
    """
    Direct interface between DB and application

    """

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def dict_to_string(dict):
        """
        Generates string ready to save in file from dictonary entry
        :param dict: req
        :return: string
        """

        for key in dict:
            req_string = str(dict[key])

        return req_string

    @staticmethod
    def string_to_dict(string):
        """
        Generates string ready to save in file from dictonary entry
        :param string: req
        :return: string
        """

        param_list = string.split(',')
        if len(param_list) != 8:
            raise ValueError("Inconsistent param amount:", len(param_list), " instead of 8.")

        else:
            return {int(param_list[0]): string}

    def check_db(self):
        """
        Creates db IF not yet created.
        :return:
        """

        if not os.path.exists(self.filename):
            with open(self.filename, 'a', newline='') as csvfile:
                fieldnames = ['nid', 'version', 'text', 'author', 'product', 'baseline', 'time', 'links']
                writer = csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()
                csvfile.close()
            print(self.filename, " data base created")
            return False
        else:
            print(self.filename, " data base already exists")
            return True

    def load_db(self):
        """
        Return dict based on db content
        :return:
        """
        req_dict = {}
        if self.check_db():
            with open(self.filename, 'r', newline='') as csvfile:
                # Skip header:
                csvfile.readline()
                for line in csvfile:
                    param_list = line.split(',')
                    req_dict.update({int(param_list[0]): line[:-2]})
            csvfile.close()

        return req_dict

    def load_history(self):
        """
        Return dict based on history db content
        :return:
        """
        hist_dict = {}
        if self.check_db():
            with open(self.filename, 'r', newline='') as csvfile:
                # Skip header:
                csvfile.readline()
                for line in csvfile:
                    param_list = line.split(',')
                    nid_v = str(int(param_list[0])) + "_" + str(int(param_list[1]))
                    hist_dict.update({nid_v: line[:-2]})
            csvfile.close()

        return hist_dict

    def append_to_file(self, req):
        """
        Appends requirement to database file. Function verifies
        input before the file is opened for append.

        :param req: Dictionary where key is requirement nid and
        value is a csv that contains params.
        :return:
        """

        try:
            req.keys()
        except AttributeError:
            print("Ups, input is not a dict.")
            raise

        for key in req:
            param_list = req[key].split(',')
            if len(param_list) != 8:
                raise ValueError("Inconsistent param amount:", len(param_list), " instead of 8.")
            else:
                with open(self.filename, 'a', newline='') as csvfile:
                    fieldnames = ['nid', 'version', 'text', 'author', 'product', 'baseline', 'time', 'links']
                    writer = csv.DictWriter(csvfile, fieldnames)
                    writer.writerow({'nid': key,
                                     'version': param_list[1],
                                     'text': param_list[2],
                                     'author': param_list[3],
                                     'product': param_list[4],
                                     'baseline': param_list[5],
                                     'time': param_list[6],
                                     'links': param_list[7]})
                    csvfile.close()

    def find_req_with_nid(self, nid_list, str=0):
        """
        Function verifies if requirements included in param are saved in DB, if so returns a dictionary with all data
        :param nid_list: list of nid to search for
        :return: dictionary with data in val if req exist, prompt if not
        """

        req_dict = {}

        with open(self.filename, 'r', newline='') as csvfile:
            # Skip header
            csvfile.readline()
            for line in csvfile:
                param_list = line.split(',')

                for nid in nid_list:
                    if not str:
                        if nid == int(param_list[0]):
                            req_dict.update({int(param_list[0]): line[:-2]})
                            nid_list.remove(nid)
                    else:
                        if nid == param_list[0]:
                            req_dict.update({param_list[0]: line[:-2]})
                            nid_list.remove(nid)
            csvfile.close()

        for nid in nid_list:
            req_dict.update({nid: "Requirement not found"})

        return req_dict

    def clear_database(self):
        """
        Clears DB, inputs header
        :return:
        """
        os.remove(self.filename)
        self.check_db()

    def remove_req_with_given_nid(self, nid_list):
        """
        Removes reqs with given nids
        :return:
        """

        with open(self.filename, 'r', newline='') as csvfile:
            temp_dict = {}
            csvfile.readline()
            for line in csvfile:
                temp_dict.update(self.string_to_dict(line[:-2]))
            for nid in nid_list:
                try:
                    del temp_dict[nid]
                except KeyError:
                    print("No req with given nid")
                    raise
                    pass
            csvfile.close()

        self.clear_database()
        self.append_to_file(temp_dict)


class DataBaseInputGenerator:
    """
    Generates input to be sent to DB
    """

    def __init__(self):
        self.DB = DataBaseOperations('requirement.csv')
        self.historyDB = DataBaseOperations('history.csv')
        self.Req = self.DB.load_db()
        self.Hist = self.historyDB.load_history()

    def get_last_nid(self):
        """
        Goes through DB and return last used nid
        :return: last used nid
        """
        if self.Req.keys():
            return max(list(self.Req.keys()))
        else:
            return 0

    def add_req(self, req):
        """
        Adds requirement to db.
        :return: Updated self.Reg dict
        """
        new_nid = int(self.get_last_nid()) + 1
        new_time = self.get_time()
        req.update({"nid": new_nid})
        req.update({"time": new_time})
        req_db = self.translate_req_dict_to_db_input(req)
        self.DB.append_to_file(req_db)
        self.Req.update(req_db)
        return self.Req, new_time

    def add_req_to_hist(self, req):
        """

        :param req:
        :return:
        """
        # Change key name to history format
        req_dict = self.translate_db_input_to_req_dict(req)
        hist_req = self.translate_req_dict_to_db_input(req_dict, 0)
        # Updated history db file
        self.historyDB.append_to_file(hist_req)
        self.Hist.update(hist_req)
        return self.Hist

    def update_req(self, nid, new_text, author):
        """

        :param nid:
        :param new_text:
        :param author:
        :return:
        """

        try:
            new_version = self.translate_db_input_to_req_dict({nid: self.Req[nid]})

        except KeyError as name:
            print("No requirement with given nid", name)
            raise
            return

        new_version["version"] = int(new_version["version"]) + 1
        new_version["text"] = new_text
        new_version["author"] = author
        new_version["time"] = self.get_time()
        new_version_db = self.translate_req_dict_to_db_input(new_version)
        # Remove old version from DB
        self.DB.remove_req_with_given_nid([nid])
        # Append new version
        self.DB.append_to_file(new_version_db)
        # Add old version to history db
        self.add_req_to_hist({nid: self.Req[nid]})
        # Return updated req dictionary
        self.Req.update(new_version_db)
        return self.Req, new_version["time"]

    def remove_req(self, nid_list):
        """

        :param nid_list:
        :return:
        """

        for nid in nid_list:
            self.add_req_to_hist({nid: self.Req[nid]})

        self.DB.remove_req_with_given_nid(nid_list)
        self.Req = self.DB.load_db()
        return self.Req

    def find_req(self, nid_list):
        """

        :return:
        """
        find_result = self.DB.find_req_with_nid(nid_list)
        not_found = {}
        not_found_nids = []
        for nid, value in find_result.items():
            if value == "Requirement not found":
                not_found.update({nid: value})
                not_found_nids.append(nid)
        for nid in not_found_nids:
            del find_result[nid]

        return find_result, not_found

    def find_req_in_history(self, nid_list):
        """

        :param nid_list:
        :return:
        """

        not_found = {}
        found_nids = []
        not_found_nids = []
        for nid in nid_list:
            versions = self.get_all_versions(nid)
            if not versions:
                not_found_nids.append(nid)
            else:
                for version in versions:
                    nid_v = str(nid) + "_" + str(version)
                    found_nids.append(nid_v)
        find_result = self.historyDB.find_req_with_nid(found_nids, 1)

        for nid in not_found_nids:
            not_found.update({nid: "requirement does not have any history"})

        return find_result, not_found

    def show_req(self, nid, db=1):
        """

        :param nid: nid of req, nid_v if history
        :return:
        """
        if db:
            database = self.Req
        else:
            database = self.Hist
        try:
            req_instance = self.translate_db_input_to_req_dict({nid: database[nid]})
        except KeyError as name:
            print("No requirement with given nid", name)
            raise

        print("Requirement ID: ", req_instance["nid"])
        print("Version: ", req_instance["version"])
        print("Text: ", req_instance["text"])
        print("Author: ", req_instance["author"])
        print("Product: ", req_instance["product"])
        print("Baseline: ", req_instance["baseline"])
        print("Created: ", self.show_time(req_instance["time"]))
        print("Links: ", req_instance["links"])

        return "Status ok"

    def show_history(self, nid):
        """

        :param nid:
        :return:
        """
        versions = self.get_all_versions(nid)
        self.show_req(nid)
        for version in versions:
            if version > 0:
                nid_v = str(nid) + "_" + str(version)
                self.show_req(nid_v, 0)
        return "Status ok"

    def clear_db(self, db=1):
        """


        :param db:
        :return:
        """
        if db:
            self.DB.clear_database()
            self.Req = self.DB.load_db()
            return self.Req
        else:
            self.historyDB.clear_database()
            self.Hist = self.historyDB.load_db()
            return self.Hist

    def get_all_versions(self, nid):
        """
        :param nid:
        :return: Returns all historical requirement version numbers
        """
        versions = []
        nid_v = str(nid) + "_1"
        v = 1
        while nid_v in self.Hist:
            versions.append(v)
            v += 1
            nid_v = str(nid) + "_" + str(v)

        versions.sort(reverse=True)
        return versions

    @staticmethod
    def translate_req_dict_to_db_input(req, db=1):
        """
        Returns a req ready to place in db
        :return:
        """
        if db:
            db_key = req["nid"]
        else:
            db_key = str(req["nid"]) + "_" + str(req["version"])
        db_list = ""
        db_list += str(req["nid"]) + ","
        db_list += str(req["version"]) + ","
        db_list += str(req["text"]) + ","
        db_list += str(req["author"]) + ","
        db_list += str(req["product"]) + ","
        db_list += str(req["baseline"]) + ","
        db_list += str(req["time"]) + ","
        db_list += str(req["links"])

        req_db = {db_key: db_list}
        return req_db

    @staticmethod
    def get_time():
        """
        Returns current time in epoch float
        :return:
        """

        return time()

    @staticmethod
    def show_time(time_float):
        """
        Returns printable view of ctime.
        :return: printable string
        """
        printable_time = strftime("%d %b %Y %H:%M:%S", gmtime(time_float))
        return printable_time

    @staticmethod
    def translate_db_input_to_req_dict(req_db):
        """
        Translates db input into
        :param req_db:
        :return:
        """
        params = list(req_db.values())
        params = params[0].split(',')
        req_dict = {"nid": int(params[0])}
        req_dict.update({"version": int(params[1])})
        req_dict.update({"text": str(params[2])})
        req_dict.update({"author": str(params[3])})
        req_dict.update({"product": float(params[4])})
        req_dict.update({"baseline": int(params[5])})
        req_dict.update({"time": float(params[6])})
        req_dict.update({"links": str(params[7])})

        return req_dict
