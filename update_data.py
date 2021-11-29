import argparse
import logging
import sqlite3

from sparql import (
    ENTITY_URL_PREFIX,
    fetch_items,
    fetch_labels,
    fetch_statements,
    sparql,
    values_query,
)


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


def insert(cur, tbl_name, row, replace=False):
    statement = "INSERT"
    if replace:
        statement = "REPLACE"
    keys = row.keys()
    col_names = ", ".join(keys)
    value_names = ", ".join(":" + k for k in keys)
    sql = "{} INTO {} ({}) VALUES ({})".format(
        statement, tbl_name, col_names, value_names
    )
    cur.execute(sql, row)


def upsert(con, pk_name, pk_value, sk_name, sk_value):
    sql = "SELECT * FROM items WHERE {} = ? OR {} = ?;".format(
        pk_name,
        sk_name,
    )
    rows = con.execute(sql, (pk_value, sk_value)).fetchall()

    if len(rows) == 0:
        cur = con.cursor()
        sql = "INSERT INTO items ({}, {}) VALUES (?, ?);".format(
            pk_name,
            sk_name,
        )
        cur.execute(sql, (pk_value, sk_value))
        assert cur.rowcount == 1
        con.commit()
    if len(rows) == 1:
        row = rows[0]
        if row[pk_name] == pk_value and row[sk_name] == sk_value:
            return
        cur = con.cursor()
        sql = "UPDATE items SET {} = ?, {} = ? WHERE {} = ? OR {} = ?;".format(
            pk_name, sk_name, pk_name, sk_name
        )
        cur.execute(sql, (pk_value, sk_value, pk_value, sk_value))
        assert cur.rowcount == 1
        con.commit()
    else:
        cur = con.cursor()
        new_row = {}
        for row in rows:
            for key in row.keys():
                if row[key]:
                    new_row[key] = row[key]
        insert(cur, "items", new_row, replace=True)
        assert cur.rowcount == 1
        con.commit()


def update_wikidata_items(con):
    sql = "SELECT wikidata FROM items"
    rows = con.execute(sql)
    qids = set([qid for (qid,) in rows])

    items = fetch_statements(
        qids,
        {
            "P345",
            "P4947",
            "P4983",
            "P9586",
            "P9751",
        },
    )

    for qid in items:
        item = items[qid]

        if "P345" in item and len(item["P345"]) == 1:
            imdb = item["P345"][0]
            upsert(con, "wikidata", qid, "imdb", imdb)

        if "P4947" in item and "P4983" not in item and len(item["P4947"]) == 1:
            tmdb = item["P4947"][0]
            upsert(con, "wikidata", qid, "tmdb_id", tmdb)

        if "P4983" in item and "P4947" not in item and len(item["P4983"]) == 1:
            tmdb = item["P4983"][0]
            upsert(con, "wikidata", qid, "tmdb_id", tmdb)

        if "P9586" in item and "P9751" not in item and len(item["P9586"]) == 1:
            appletv = item["P9586"][0]
            upsert(con, "wikidata", qid, "appletv", appletv)

        if "P9751" in item and "P9586" not in item and len(item["P9751"]) == 1:
            appletv = item["P9751"][0]
            upsert(con, "wikidata", qid, "appletv", appletv)

    items = fetch_labels(qids)
    for qid in items:
        label = items[qid]
        con.execute(
            "UPDATE items SET title = ? WHERE wikidata = ?;",
            (label, qid),
        )

    items = fetch_tomatometer(qids)
    for qid in items:
        score = items[qid]
        con.execute(
            "UPDATE items SET tomatometer = ? WHERE wikidata = ?;",
            (score, qid),
        )

    con.commit()


def fetch_tomatometer(qids):
    query = "SELECT ?item ?tomatometer WHERE { "
    query += values_query(qids)
    query += """
      ?item p:P444 [ pq:P459 wd:Q108403393; ps:P444 ?tomatometer ].
    }
    """

    items = {}

    for result in sparql(query):
        qid = result["item"]["value"].replace(ENTITY_URL_PREFIX, "")
        score = int(result["tomatometer"]["value"].replace("%", ""))
        items[qid] = score

    return items


def find_missing_wikidata_qids(con):
    rows = con.execute("SELECT imdb FROM items WHERE wikidata IS NULL")
    imdb_ids = set([imdb for (imdb,) in rows])

    if len(imdb_ids) == 0:
        return

    items = fetch_items("P345", imdb_ids)

    for qid in items:
        imdb_id = items[qid]
        upsert(con, "imdb", imdb_id, "wikidata", qid)

    con.commit()


if __name__ == "__main__":
    main()
