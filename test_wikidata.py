from wikidata import (
    fetch_items,
    fetch_labels,
    fetch_statements,
    fetch_tomatometer,
    sparql,
)


def test_sparql():
    results = sparql(
        """
        SELECT ?item ?itemLabel WHERE {
          ?item wdt:P31 wd:Q146.
          SERVICE wikibase:label {
            bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
          }
        }
        LIMIT 10
        """
    )
    assert len(results) == 10
    assert results[0]["item"]["value"]
    assert results[0]["itemLabel"]["value"]


def test_fetch_statements():
    items = fetch_statements({"Q172241"}, {"P345", "P4947"})
    assert len(items) == 1

    item = items["Q172241"]
    assert item
    assert item["P345"]
    assert item["P4947"]


def test_fetch_labels():
    items = fetch_labels({"Q172241"})
    assert len(items) == 1

    assert items["Q172241"] == "The Shawshank Redemption"


def test_fetch_items():
    items = fetch_items("P345", {"tt0068646", "tt0111161"})
    assert len(items) == 2

    assert items["Q47703"] == "tt0068646"
    assert items["Q172241"] == "tt0111161"


def test_fetch_tomatometer():
    items = fetch_tomatometer({"Q172241"})
    assert len(items) == 1

    assert items["Q172241"] == 91
