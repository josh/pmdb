import logging

import requests

ENTITY_URL_PREFIX = "http://www.wikidata.org/entity/"
PROP_URL_PREFIX = "http://www.wikidata.org/prop/"

sparql_url = "https://query.wikidata.org/sparql"

sparql_headers = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    + "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    + "Version/14.1.2 "
    + "Safari/605.1.15",
}


def sparql(query):
    logging.debug("SPARQL\n{}".format(query))
    data = {"query": query}
    r = requests.post(sparql_url, headers=sparql_headers, data=data)
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def sparql_batch_items(query_template, qids, batch_size):
    assert "?items" in query_template
    for qid_batch in batches(qids, size=batch_size):
        query = query_template.replace("?items", values_query(qid_batch))
        yield from sparql(query)


def fetch_statements(qids, properties):
    items = {}

    query = """
    SELECT ?item ?property ?value WHERE {
      ?items
      OPTIONAL {
        ?item ?property ?statement.
        ?statement ?ps ?value.
        ?statement wikibase:rank ?rank.
        FILTER(?rank != wikibase:DeprecatedRank)
      }
    """
    query += "FILTER("
    ps = ["(?ps = ps:" + p + ")" for p in properties]
    query += " || ".join(ps) + ")"
    query += " }"

    results = sparql_batch_items(query, qids, batch_size=500)
    for result in results:
        qid = extract_qid(result["item"]["value"])
        prop = result["property"]["value"].replace(PROP_URL_PREFIX, "")
        value = result["value"]["value"]

        item = items[qid] = items.get(qid, {})
        properties = item[prop] = item.get(prop, [])

        properties.append(value)

    return items


def fetch_labels(qids):
    items = {}

    query = """
      SELECT ?item ?itemLabel WHERE {
        ?items
        SERVICE wikibase:label {
          bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
        }
      }
    """

    results = sparql_batch_items(query, qids, batch_size=1000)
    for result in results:
        qid = extract_qid(result["item"]["value"])
        label = result["itemLabel"]["value"]
        items[qid] = label
        assert qid in qids, "{} not in requested set".format(qid)

    return items


def fetch_items(property, values):
    items = {}
    nonunique = set()

    def fetch(values):
        quoted_values = " ".join('"{}"'.format(value) for value in values)

        query = "SELECT ?item ?value WHERE { "
        query += "VALUES ?value { " + quoted_values + " } "
        query += "?item wdt:" + property + " ?value. }"

        for result in sparql(query):
            qid = extract_qid(result["item"]["value"])
            value = result["value"]["value"]

            if qid in items:
                nonunique.add(qid)

            items[qid] = value

    for value_batch in batches(values, size=500):
        fetch(value_batch)

    for qid in nonunique:
        del items[qid]

    return items


def fetch_tomatometer(qids):
    items = {}

    def fetch(qids):
        query = "SELECT ?item ?tomatometer WHERE { "
        query += values_query(qids)
        query += """
          ?item p:P444 [ pq:P459 wd:Q108403393; ps:P444 ?tomatometer ].
        }
        """

        for result in sparql(query):
            qid = extract_qid(result["item"]["value"])
            score = int(result["tomatometer"]["value"].replace("%", ""))
            items[qid] = score

    for qid_batch in batches(qids, size=1000):
        fetch(qid_batch)

    return items


def extract_qid(uri):
    assert uri.startswith(ENTITY_URL_PREFIX)
    return uri.replace(ENTITY_URL_PREFIX, "")


def values_query(qids, binding="item"):
    values = " ".join("wd:{}".format(qid) for qid in qids)
    return "VALUES ?" + binding + " { " + values + " }"


def batches(iterable, size):
    batch = []

    for element in iterable:
        batch.append(element)
        if len(batch) == size:
            yield batch
            batch = []

    if batch:
        yield batch


media_properties = {
    "P345",
    "P1258",
    "P2047",
    "P4947",
    "P4983",
    "P9586",
    "P9751",
}


def fetch_media_items(qids):
    items = {}
    for qid in qids:
        items[qid] = {}

    statements = fetch_statements(qids, media_properties)
    for qid in statements:
        item = statements[qid]

        if exists_once(item, "P345"):
            items[qid]["imdb_id"] = item["P345"][0]

        if exists_once(item, "P1258"):
            items[qid]["rottentomatoes_id"] = item["P1258"][0]

        if exists_once(item, "P2047"):
            items[qid]["duration"] = int(float(item["P2047"][0]))

        if exists_once(item, "P4947") and "P4983" not in item:
            items[qid]["tmdb_type"] = "movie"
            items[qid]["tmdb_id"] = int(item["P4947"][0])
        elif exists_once(item, "P4983") and "P4947" not in item:
            items[qid]["tmdb_type"] = "tv"
            items[qid]["tmdb_id"] = int(item["P4983"][0])

        if exists_once(item, "P9586") and "P9751" not in item:
            items[qid]["appletv_id"] = item["P9586"][0]
        elif exists_once(item, "P9751") and "P9586" not in item:
            items[qid]["appletv_id"] = item["P9751"][0]

    labels = fetch_labels(qids)
    for qid in labels:
        items[qid]["title"] = labels[qid]

    scores = fetch_tomatometer(qids)
    for qid in scores:
        items[qid]["tomatometer"] = scores[qid]

    return items


def exists_once(obj, key):
    return key in obj and len(obj[key]) == 1
