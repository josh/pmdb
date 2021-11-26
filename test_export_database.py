from export_database import clean_dict


def test_clean_dict():
    d1 = {"foo": 42, "bar": None}
    d2 = clean_dict(d1)

    assert d1["foo"] == 42
    assert "bar" in d1

    assert d2["foo"] == 42
    assert "bar" not in d2
