from app.controller.global_config import GlobalConfig, GlobalConfigDatabase
import pytest, os

# global config Object
@pytest.fixture
def gc():
    return GlobalConfig()

@pytest.fixture
def gdb():
    gdb = GlobalConfigDatabase()
    default_values = {
        "test_AAA" : "AAA",
        "test_BBB" : "BBB",
        "test_CCC" : "",
        "test_DDD" : None,
        "test_EEE" : True,
        "test_FFF" : 2,
        "test_GGG" : 3.4
    }
    gdb.init_data(default_values)
    yield gdb
    # tear down
    # remove test data
    for k in default_values:
        gdb.delete(k)

def test_gdb_write(gdb):
    # string
    gdb.update("test_AAA","ABC")
    assert gdb.read("test_AAA") == "ABC"
    # integer
    gdb.update("test_BBB", 2)
    assert gdb.read("test_BBB") == "2"
    # float
    gdb.update("test_BBB", 2.34)
    assert gdb.read("test_BBB") == "2.34"
    # boolean
    gdb.update("test_BBB", True)
    assert gdb.read("test_BBB") == "True"

def test_gdb_read(gdb):
    assert gdb.read("test_AAA") == "AAA"
    assert gdb.read("test_BBB") == "BBB"
    assert gdb.read("test_CCC") == ""
    assert gdb.read("test_DDD") == None
    # Booleen, number will be stored as String
    assert gdb.read("test_EEE") == "True"
    assert gdb.read("test_FFF") == "2"
    assert gdb.read("test_GGG") == "3.4"

def test_gc_get(gc):
    # _RESTART_LOCK {True | False}
    # There's a convention for True | False value :"True" -> True
    lock = gc.get("_RESTART_LOCK")
    assert lock == True or lock == False
