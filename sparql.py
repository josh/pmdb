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
