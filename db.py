ITEMS_PRIMARY_KEYS = [
    "wikidata_qid",
    "imdb_id",
    ["tmdb_type", "tmdb_id"],
    ["trakt_type", "trakt_id"],
    "appletv_id",
]


def items_upsert(con, row, overwrite=True):
    upsert(con, "items", ITEMS_PRIMARY_KEYS, row, overwrite)


def upsert(con, tbl_name, pks, row, overwrite=True):
    cur = con.cursor()

    pks = filter_pks(pks, row)
    where_clause = make_where_clause(pks)
    sql = "SELECT * FROM {} WHERE {}".format(tbl_name, where_clause)
    existing_rows = cur.execute(sql, row).fetchall()

    if overwrite:
        row = merge_rows(*existing_rows, row)
    else:
        row = merge_rows(row, *existing_rows)

    keys = row.keys()
    col_names = ", ".join(keys)
    value_names = ", ".join(":" + k for k in keys)
    sql = "REPLACE INTO {} ({}) VALUES ({})".format(tbl_name, col_names, value_names)

    cur.execute(sql, row)
    con.commit()


def filter_pks(pks, row):
    for pk in pks:
        if type(pk) is list:
            if all(k in row for k in pk):
                yield pk
        else:
            if pk in row:
                yield pk


def make_where_clause(keys):
    def match_clause(key):
        return "{} = :{}".format(key, key)

    def combine_clauses(keys):
        for key in keys:
            if type(key) is list:
                yield "(" + " AND ".join(match_clause(k) for k in key) + ")"
            else:
                yield match_clause(key)

    return " OR ".join(combine_clauses(keys))


def merge_rows(*rows):
    new_row = {}
    for row in rows:
        for key in row.keys():
            if row[key] is None:
                continue
            new_row[key] = row[key]
    return new_row
