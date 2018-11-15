import csv
import os.path


class DataBaseOperations:

    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def dict_to_string(dict):
        """
        Generates string ready to save in file from dictionary entry
        :param dict: req
        :return: string
        """

        for key in dict:
            req_string = str(dict[key])

        return req_string

    @staticmethod
    def string_to_dict(string):
        """
        Generates string ready to save in file from dictionary entry
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
        :return: True if already exists or False if created for test purposes.
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
        Method loads requirement DB into dictionary.
        :return: Return dict based on db content.
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
        Method loads history DB into dictionary.
        :return: Return dict based on db content.
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
        :param str: specified key type if set key is string, otherwise int.
        :return: dictionary with data in val if req exist, prompt if not.
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
        """
        os.remove(self.filename)
        self.check_db()

    def remove_req_with_given_nid(self, nid_list):
        """
        Method removes requirements included in nid_list from DB.
        :param nid_list: List of requirements nids to be removed from DB.
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



