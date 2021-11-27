from export_database import clean_dict, get_value


def test_clean_dict():
    d1 = {"foo": 42, "bar": None}
    d2 = clean_dict(d1)

    assert d1["foo"] == 42
    assert "bar" in d1

    assert d2["foo"] == 42
    assert "bar" not in d2


def test_get_value():
    obj = {"foo": 1, "bar": {"baz": 2, "qux": {"quux": 3}}}
    assert get_value(obj, ["foo"]) == 1
    assert get_value(obj, ["bar", "baz"]) == 2
    assert get_value(obj, ["bar", "qux"]) == {"quux": 3}
    assert get_value(obj, ["bar", "qux", "quux"]) == 3
