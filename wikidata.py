import logging

import requests

ENTITY_URL_PREFIX = "http://www.wikidata.org/entity/"
PROP_URL_PREFIX = "http://www.wikidata.org/prop/"


def sparql(query):
    logging.debug("SPARQL\n{}".format(query))
    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        + "Version/14.1.2 "
        + "Safari/605.1.15",
    }
    data = {"query": query}
    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def fetch_statements(qids, properties):
    items = {}

    query_prefix = "SELECT ?item ?property ?value WHERE { "
    query_suffix = """
    OPTIONAL {
      ?item ?property ?statement.
      ?statement ?ps ?value.
      ?statement wikibase:rank ?rank.
      FILTER(?rank != wikibase:DeprecatedRank)
    }
     """
    query_suffix += "FILTER("
    ps = ["(?ps = ps:" + p + ")" for p in properties]
    query_suffix += " || ".join(ps) + ")"
    query_suffix += "}"

    def fetch(qids):
        query = query_prefix + values_query(qids) + query_suffix
        for result in sparql(query):
            qid = extract_qid(result["item"]["value"])
            prop = result["property"]["value"].replace(PROP_URL_PREFIX, "")
            value = result["value"]["value"]

            item = items[qid] = items.get(qid, {})
            properties = item[prop] = item.get(prop, [])

            properties.append(value)

    for qid_batch in batches(qids, size=500):
        fetch(qid_batch)

    return items


def fetch_labels(qids):
    items = {}

    def fetch(qids):
        query = "SELECT ?item ?itemLabel WHERE { "
        query += values_query(qids)
        query += """
          SERVICE wikibase:label {
            bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
          }
        }
        """

        for result in sparql(query):
            qid = extract_qid(result["item"]["value"])
            label = result["itemLabel"]["value"]
            items[qid] = label

    for qid_batch in batches(qids, size=500):
        fetch(qid_batch)

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
            qid = result["item"]["value"].replace(ENTITY_URL_PREFIX, "")
            score = int(result["tomatometer"]["value"].replace("%", ""))
            items[qid] = score

    for qid_batch in batches(qids, size=500):
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
