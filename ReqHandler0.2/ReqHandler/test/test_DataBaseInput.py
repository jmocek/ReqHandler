from module_file.module_db_operations import *
import pytest
import os.path


@pytest.fixture
def dbi(request):
    dbi = DataBaseInputGenerator()

    def cleanup():
        os.remove('requirement.csv')
        os.remove('history.csv')
    request.addfinalizer(cleanup)
    return dbi


def test_add_req(dbi):
    test_req1 = {"version": 5, "text": "test1",
                 "author": "jm", "product": 1.1, "baseline": 3, "links": []}
    test_req2 = {"version": 7, "text": "test1",
                 "author": "jm", "product": 1.2, "baseline": 3, "links": []}
    test_req, now = dbi.add_req(test_req1)
    test_req, now2 = dbi.add_req(test_req2)

    txt = "1,5,test1,jm,1.1,3," + str(now) + ",[]"
    txt2 = "2,7,test1,jm,1.2,3," + str(now2) + ",[]"
    print(test_req)
    assert test_req[1] == txt and test_req[2] == txt2


def test_get_last_nid(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    last_nid = dbi.get_last_nid()
    assert last_nid == 10


def test_get_last_nid_empty(dbi):
    last_nid = dbi.get_last_nid()
    assert last_nid == 0


def test_add_to_hist_db(dbi):
    test_req = {1: "1,1231,this is test,muhamad ali,1.1,5,12341234.123,[]"}
    test_hist_input = dbi.add_req_to_hist(test_req)
    nid_v = "1_1231"
    assert test_req[1] == test_hist_input[nid_v]


def test_update_req(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    req, now = dbi.update_req(9, "newer txt", "john cena")
    txt = "9,6,newer txt,john cena,1.1,3," + str(now) + ",[]"
    assert req[9] == txt and dbi.Req[9] == txt


def test_update_req_no_req(dbi):
    with pytest.raises(KeyError):
        dbi.update_req(9, "newer txt", "john cena")


def test_remove_req(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dict_after_remove = dbi.remove_req([8, 9])
    nid_list_req = list(dict_after_remove.keys())
    nid_list_hist = list(dbi.Hist.keys())
    assert 8 not in nid_list_req and 9 not in nid_list_req
    assert "8_5" in nid_list_hist and "9_5" in nid_list_hist


def test_remove_req_not_exist(dbi):
    with pytest.raises(KeyError):
        dbi.remove_req([9])


def test_find_all_found(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    found, not_found = dbi.find_req([2, 3])
    assert 2 and 3 in found and not not_found


def test_find_found_and_not_found(dbi):
    test_req = {"version": 1, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    found, not_found = dbi.find_req([2, 3, 11, 12])
    assert 2 in found
    assert 3 in found
    assert 11 not in found
    assert 12 not in found
    assert 11 in not_found
    assert 12 in not_found


def test_show_req_reqdb(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    status1 = dbi.show_req(1)
    status2 = dbi.show_req(7)

    assert status1 == "Status ok"
    assert status2 == "Status ok"


def test_show_req_histdb(dbi):
    test_req = {"version": 5, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dbi.remove_req([2, 4, 6, 8, 10])

    status1 = dbi.show_req("2_5", 0)
    status2 = dbi.show_req("4_5", 0)

    assert status1 == "Status ok"
    assert status2 == "Status ok"


def test_show_req_no_req(dbi):
    with pytest.raises(KeyError):
        dbi.show_req(1)
        dbi.show_req("1_1", 0)


def test_get_all_versions_2_versions(dbi):
    test_req = {"version": 1, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dbi.update_req(9, "newer txt", "john cena")
    dbi.update_req(9, "newer txt2", "john cena2")

    versions = dbi.get_all_versions(9)
    assert versions == [2, 1]


def test_get_all_versions_no_versions(dbi):
    versions = dbi.get_all_versions(9)
    assert len(versions) == 0


def test_show_history(dbi):
    test_req = {"version": 1, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dbi.update_req(9, "newer txt", "john cena")
    dbi.update_req(9, "newer txt2", "john cena2")

    assert dbi.show_history(9) == "Status ok"


def test_clear_db(dbi):
    test_req = {"version": 1, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dbi.update_req(9, "newer txt", "john cena")
    dbi.update_req(9, "newer txt2", "john cena2")

    req = dbi.clear_db()
    hist = dbi.clear_db(0)
    assert req == {}
    assert hist == {}


def test_find_in_history(dbi):
    test_req = {"version": 1, "text": "test1",
                "author": "jm", "product": 1.1, "baseline": 3, "links": []}

    for x in range(10):
        dbi.add_req(test_req)

    dbi.update_req(2, "newer txt", "john cena")
    dbi.update_req(3, "newer txt2", "john cena2")
    dbi.update_req(9, "newer txt", "john cena")
    dbi.update_req(9, "newer txt2", "john cena2")

    found, not_found = dbi.find_req_in_history([2, 3, 8, 9])
    assert "2_1" in found
    assert "3_1" in found
    assert "2_2" not in found
    assert "9_1" in found
    assert "9_2" in found
    assert 8 in not_found
    assert "8_1" not in found
    assert "8_1" not in not_found
