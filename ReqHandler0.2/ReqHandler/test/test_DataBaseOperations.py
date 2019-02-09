from module_file.module_file import *
import os
import csv
import pytest


@pytest.fixture
def db(request):
    db = DataBaseOperations('test.csv')
    db.check_db()
    with open('test.csv', 'a', newline='') as csvfile:
        fieldnames = ['nid', 'version', 'text', 'author', 'product', 'baseline', 'time', 'links']
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writerow({'nid': 112,
                         'version': 1,
                         'text': "text",
                         'author': "jm",
                         'product': 1.0,
                         'baseline': 1,
                         'time': 123123.12312,
                         'links': []})
        writer.writerow({'nid': 111,
                         'version': 1,
                         'text': "text",
                         'author': "jm",
                         'product': 1.0,
                         'baseline': 1,
                         'time': 123123.12312,
                         'links': []})
        csvfile.close()

    def cleanup():
        os.remove('test.csv')
    request.addfinalizer(cleanup)
    return db


def test_string_from_dict_req(db):
    req_string = "1,1,text,jm,1.0,1,123123.123,[]"
    req_dict = {1: "1,1,text,jm,1.0,1,123123.123,[]"}

    assert db.dict_to_string(req_dict) == req_string


def test_string_to_dict_valid(db):
    req_string = "1,1,text,jm,1.0,1,123123.123,[]"
    req_dict = {1: "1,1,text,jm,1.0,1,123123.123,[]"}

    assert db.string_to_dict(req_string) == req_dict


def test_string_to_dict_invalid(db):
    req_string = "1,1text,jm,1.0,1,123123.123,[]"

    with pytest.raises(ValueError):
        db.string_to_dict(req_string)


def test_check_db():
    db_check = DataBaseOperations('test.csv')
    exist = db_check.check_db()
    with open('test.csv', 'r+', newline='') as csvfile:
                txt = csvfile.read()
                csvfile.close()
                os.remove('test.csv')
    assert "nid,version,text,author,product,baseline,time,links\r\n" == txt
    assert exist is False


def test_check_db_exist(db):
    exist = db.check_db()
    assert exist is True


def test_find_req_in_file(db):

    req = db.find_req_with_nid([111, 112])
    assert req == {112: "112,1,text,jm,1.0,1,123123.12312,[]", 111: "111,1,text,jm,1.0,1,123123.12312,[]"}


def test_find_req_in_file_no_req_in_file(db):
    req = db.find_req_with_nid([113])
    assert req == {113: "Requirement not found"}


def test_append_req_to_file(db):
    req = {'421': '421,2,text,jm,1.0,1,123123.123,[]'}
    db.append_to_file(req)
    with open(db.filename, "rb") as f:
        for last in f:

            pass  # Loop through the whole file reading it all.
    assert b'421,2,text,jm,1.0,1,123123.123,[]\r\n' == last


def test_append_req_to_file_inconsistent_req(db):
    req = {'111': 'not,enough,params'}
    with pytest.raises(ValueError):
        db.append_to_file(req)


def test_append_req_to_file_not_a_dict(db):
    req = "definitely not a dictionary"
    with pytest.raises(Exception):
        db.append_to_file(req)


def test_clear_db_operation(db):

    db.clear_database()
    with open('test.csv', 'r', newline='') as csvfile:
        lines = []
        for line in csvfile:
            lines.append(line)
        csvfile.close()
    assert len(lines) == 1
    assert lines[0] == "nid,version,text,author,product,baseline,time,links\r\n"


def test_remove_nid_with_given_nid(db):
    nid_list = [111]
    db.remove_req_with_given_nid(nid_list)
    with open('test.csv', 'r', newline='') as csvfile:
        lines = []
        for line in csvfile:
            lines.append(line)
        csvfile.close()
    assert len(lines) == 2
    assert lines[0] == "nid,version,text,author,product,baseline,time,links\r\n"
    assert lines[1] == "112,1,text,jm,1.0,1,123123.12312,[]\r\n"


def test_remove_unknown_nid(db):
    nid_list = [113]
    with pytest.raises(KeyError):
        db.remove_req_with_given_nid(nid_list)


def test_load_db(db):
    req_dict = db.load_db()
    assert req_dict == {112: "112,1,text,jm,1.0,1,123123.12312,[]", 111: "111,1,text,jm,1.0,1,123123.12312,[]"}


def test_load_db_hist(db):
    req_dict = db.load_history()
    assert req_dict == {"112_1": "112,1,text,jm,1.0,1,123123.12312,[]", "111_1": "111,1,text,jm,1.0,1,123123.12312,[]"}
