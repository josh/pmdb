from wikidata import (
    fetch_items,
    fetch_labels,
    fetch_media_items,
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


def test_fetch_media_items():
    items = fetch_media_items({"Q172241", "Q1079"})
    assert len(items) == 2

    item = items["Q172241"]
    assert item["wikidata_qid"] == "Q172241"
    assert item["imdb_id"] == "tt0111161"
    assert item["tmdb_type"] == "movie"
    assert item["tmdb_id"] == 278
    assert item["appletv_id"] == "umc.cmc.459n4f98t82t8ommdoa7ebnny"
    assert item["title"] == "The Shawshank Redemption"
    assert item["year"] == 1994
    assert item["director"] == "Frank Darabont"
    assert item["duration"] == 142
    assert item["rottentomatoes_id"] == "m/shawshank_redemption"
    assert item["tomatometer"] == 91

    item = items["Q1079"]
    assert item["wikidata_qid"] == "Q1079"
    assert item["imdb_id"] == "tt0903747"
    assert item["tmdb_type"] == "tv"
    assert item["tmdb_id"] == 1396
    assert item["appletv_id"] == "umc.cmc.1v90fu25sgywa1e14jwnrt9uc"
    assert item["title"] == "Breaking Bad"
