import requests


def sparql(query):
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


ENTITY_URL_PREFIX = "http://www.wikidata.org/entity/"
PROP_URL_PREFIX = "http://www.wikidata.org/prop/"


def fetch_statements(qids, properties):
    query = "SELECT ?item ?property ?value WHERE { "
    query += values_query(qids)
    query += """
    OPTIONAL {
      ?item ?property ?statement.
      ?statement ?ps ?value.
      ?statement wikibase:rank ?rank.
      FILTER(?rank != wikibase:DeprecatedRank)
    }
    """
    query += "FILTER("
    query += " || ".join(["(?ps = ps:" + p + ")" for p in properties]) + ")"
    query += "}"

    items = {}

    for result in sparql(query):
        qid = result["item"]["value"].replace(ENTITY_URL_PREFIX, "")
        prop = result["property"]["value"].replace(PROP_URL_PREFIX, "")
        value = result["value"]["value"]

        item = items[qid] = items.get(qid, {})
        properties = item[prop] = item.get(prop, [])

        properties.append(value)

    return items


def fetch_labels(qids):
    query = "SELECT ?item ?itemLabel WHERE { "
    query += values_query(qids)
    query += """
      SERVICE wikibase:label {
        bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
      }
    }
    """

    items = {}

    for result in sparql(query):
        qid = result["item"]["value"].replace(ENTITY_URL_PREFIX, "")
        label = result["itemLabel"]["value"]
        items[qid] = label

    return items


def values_query(qids, binding="item"):
    values = " ".join("wd:{}".format(qid) for qid in qids)
    return "VALUES ?" + binding + " { " + values + " }"


def fetch_items(property, values):
    quoted_values = " ".join('"{}"'.format(value) for value in values)

    query = "SELECT ?item ?value WHERE { "
    query += "VALUES ?value { " + quoted_values + " } "
    query += "?item wdt:" + property + " ?value. }"

    items = {}

    for result in sparql(query):
        qid = result["item"]["value"].replace(ENTITY_URL_PREFIX, "")
        value = result["value"]["value"]
        items[qid] = value

    return items
