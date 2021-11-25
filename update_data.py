import argparse
import logging
import sqlite3

from sparql import fetch_statements


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
    rows = con.execute("SELECT wikidata FROM items")
    qids = set([qid for (qid,) in rows])

    items = fetch_statements(qids, {"P345", "P1476", "P4947", "P4983"})

    for qid in items:
        item = items[qid]

        if "P345" in item and len(item["P345"]) == 1:
            imdb = item["P345"][0]
            con.execute(
                "UPDATE items SET imdb = ? WHERE wikidata = ?;",
                (imdb, qid),
            )

        if "P4947" in item and "P4983" not in item and len(item["P4947"]) == 1:
            tmdb = item["P4947"][0]
            con.execute(
                "UPDATE items SET tmdb = ? WHERE wikidata = ?;",
                (tmdb, qid),
            )

        if "P4983" in item and "P4947" not in item and len(item["P4983"]) == 1:
            tmdb = item["P4983"][0]
            con.execute(
                "UPDATE items SET tmdb = ? WHERE wikidata = ?;",
                (tmdb, qid),
            )

    con.commit()


if __name__ == "__main__":
    main()
