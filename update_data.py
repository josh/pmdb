import argparse
import logging
import sqlite3

from db import items_upsert
from wikidata import fetch_items, fetch_labels, fetch_statements, fetch_tomatometer


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
    sql = "SELECT wikidata_qid FROM items"
    rows = con.execute(sql)
    qids = set([qid for (qid,) in rows])

    items = fetch_statements(
        qids,
        {
            "P345",
            "P2047",
            "P4947",
            "P4983",
            "P9586",
            "P9751",
        },
    )

    for qid in items:
        item = items[qid]

        if "P345" in item and len(item["P345"]) == 1:
            imdb_id = item["P345"][0]
            row = {"wikidata_qid": qid, "imdb_id": imdb_id}
            items_upsert(con, row)

        if "P2047" in item and len(item["P2047"]) == 1:
            duration = int(float(item["P2047"][0]))
            con.execute(
                "UPDATE items SET duration = ? WHERE wikidata_qid = ?;",
                (duration, qid),
            )

        if "P4947" in item and "P4983" not in item and len(item["P4947"]) == 1:
            tmdb_id = item["P4947"][0]
            row = {"wikidata_qid": qid, "tmdb_type": "movie", "tmdb_id": tmdb_id}
            items_upsert(con, row)

        if "P4983" in item and "P4947" not in item and len(item["P4983"]) == 1:
            tmdb_id = item["P4983"][0]
            row = {"wikidata_qid": qid, "tmdb_type": "tv", "tmdb_id": tmdb_id}
            items_upsert(con, row)

        if "P9586" in item and "P9751" not in item and len(item["P9586"]) == 1:
            appletv_id = item["P9586"][0]
            row = {"wikidata_qid": qid, "appletv_id": appletv_id}
            items_upsert(con, row)

        if "P9751" in item and "P9586" not in item and len(item["P9751"]) == 1:
            appletv_id = item["P9751"][0]
            row = {"wikidata_qid": qid, "appletv_id": appletv_id}
            items_upsert(con, row)

    items = fetch_labels(qids)
    for qid in items:
        label = items[qid]
        con.execute(
            "UPDATE items SET title = ? WHERE wikidata_qid = ?;",
            (label, qid),
        )

    items = fetch_tomatometer(qids)
    for qid in items:
        score = items[qid]
        con.execute(
            "UPDATE items SET tomatometer = ? WHERE wikidata_qid = ?;",
            (score, qid),
        )

    con.commit()


def find_missing_wikidata_qids(con):
    rows = con.execute("SELECT imdb_id FROM items WHERE wikidata_qid IS NULL")
    imdb_ids = set([imdb for (imdb,) in rows])

    if len(imdb_ids) == 0:
        return

    items = fetch_items("P345", imdb_ids)

    for qid in items:
        imdb_id = items[qid]
        row = {"wikidata_qid": qid, "imdb_id": imdb_id}
        items_upsert(con, row)

    con.commit()


if __name__ == "__main__":
    main()
