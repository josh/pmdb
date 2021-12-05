import argparse
import logging
import sqlite3

from db import items_upsert
from wikidata import fetch_items, fetch_media_items


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

    find_missing_wikidata_qids(con)
    update_wikidata_items(con)


def update_wikidata_items(con):
    sql = "SELECT wikidata_qid FROM items WHERE wikidata_qid IS NOT NULL"
    rows = con.execute(sql)
    qids = set([qid for (qid,) in rows])
    items = fetch_media_items(qids)
    for qid in items:
        items_upsert(con, items[qid], overwrite=True)
    con.commit()


def find_missing_wikidata_qids(con):
    rows = con.execute("SELECT imdb_id FROM items WHERE wikidata_qid IS NULL")
    imdb_ids = set([imdb for (imdb,) in rows])

    if len(imdb_ids) == 0:
        return

    items = fetch_items("P345", imdb_ids)

    for qid in items:
        imdb_id = items[qid]
        items_upsert(con, {"wikidata_qid": qid, "imdb_id": imdb_id})

    con.commit()


if __name__ == "__main__":
    main()
