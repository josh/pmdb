from db import make_where_clause


def test_make_where_clause():
    assert make_where_clause(["foo"]) == "foo = :foo"
    assert make_where_clause(["foo", "bar"]) == "foo = :foo OR bar = :bar"
    assert (
        make_where_clause(["foo", "bar", "baz"])
        == "foo = :foo OR bar = :bar OR baz = :baz"
    )
    assert (
        make_where_clause(["foo", ["bar", "baz"]])
        == "foo = :foo OR (bar = :bar AND baz = :baz)"
    )
