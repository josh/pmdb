from export_database import clean_dict, get_value, insert_value


def test_insert_value():
    obj = {}

    insert_value(obj, ["foo"], 42, unique=True)
    assert obj["foo"] == 42

    insert_value(obj, ["bar"], 1, unique=False)
    insert_value(obj, ["bar"], 2, unique=False)
    assert obj["bar"] == [1, 2]

    insert_value(obj, ["baz", "bar", "foo"], 42, unique=True)
    assert obj["baz"]["bar"]["foo"] == 42


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
