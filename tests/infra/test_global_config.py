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
        "test_DDD" : None
    }
    gdb.init_data(default_values)
    yield gdb
    # tear down
    for k in default_values:
        gdb.delete(k)

def test_gdb_read(gdb):
    assert gdb.read("test_AAA") == "AAA"
    assert gdb.read("test_BBB") == "BBB"
    assert gdb.read("test_CCC") == ""
    assert gdb.read("test_DDD") == None
