import _pickle


def test_pickle_highest_protocol():
    # test wrong protocol level
    try:
        _pickle.dumps({"a": 1}, 5)
    except ValueError as e:
        assert str(e) == "pickle protocol must be <= 4"
    else:
        assert 1 == 2

    try:
        _pickle.dumps({"a": 1}, 4)
        e = None
    except ValueError as e:
        e = str(e)
    else:
        assert e is None
