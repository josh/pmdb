import argparse
import logging
import sqlite3

from sparql import sparql


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", action="store")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args = parser.parse_args()

    loglevel = {
        0: logging.ERROR,
        1: logging.WARN,
        2: logging.INFO,
        3: logging.DEBUG,
    }[args.verbose]

    logging.basicConfig(level=loglevel, format="%(message)s")
    logging.getLogger().setLevel(loglevel)

    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    update_wikidata(con)


def update_wikidata(con):
    rows = [dict(row) for row in con.execute("SELECT * FROM items;")]

    query = """
    SELECT * WHERE {
    """

    values = set()
    for row in rows:
        values.add("wd:{}".format(row["wikidata"]))
    query += "  VALUES ?item { " + " ".join(values) + " }"

    query += """
      OPTIONAL { ?item wdt:P1476 ?title. }
      OPTIONAL { ?item wdt:P345 ?imdb. }
      OPTIONAL { ?item wdt:P4947 ?tmdb_movie. }
      OPTIONAL { ?item wdt:P4983 ?tmdb_tv. }
    }
    """

    items = {}

    for result in sparql(query):
        qid = result["item"]["value"].replace("http://www.wikidata.org/entity/", "")
        imdb = result["imdb"]["value"]

        con.execute("UPDATE items SET imdb = ? WHERE wikidata = ?;", (imdb, qid))

    con.commit()


if __name__ == "__main__":
    main()
