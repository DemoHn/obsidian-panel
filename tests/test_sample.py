def double_num(x):
    return x*2

def test_double():
    assert double_num(8) == 16

def test_lt():
    assert double_num(16) < 33

def test_multi():
    assert double_num(32) == 64
    assert double_num(32) == 64.0
