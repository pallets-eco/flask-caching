import sys
import _pickle


def test_pickle_highest_protocol():
    if sys.version_info >= (3, 8):
        level = 6
    else:
        level = 5
    # test wrong protocol level
    low_level = level - 1
    try:
        _pickle.dumps({"a": 1}, level)
    except ValueError as e:
        assert str(e) == "pickle protocol must be <= {}".format(low_level)
    else:
        assert 1 == 2

    try:
        _pickle.dumps({"a": 1}, low_level)
        e = None
    except ValueError as e:
        e = str(e)
    else:
        assert e is None
