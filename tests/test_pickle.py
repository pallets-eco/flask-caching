import sys
import _pickle


def test_pickle_highest_protocol():
    if sys.version_info >= (3, 8):
        level = 6
    else:
        level = 5
    # test wrong protocol level
    try:
        _pickle.dumps({"a": 1}, level)
    except ValueError as e:
        assert str(e) == f"pickle protocol must be <= {level - 1}"
    else:
        assert 1 == 2

    try:
        _pickle.dumps({"a": 1}, level - 1)
        e = None
    except ValueError as e:
        e = str(e)
    else:
        assert e is None
