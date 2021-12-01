def upsert(con, tbl_name, pks, row):
    cur = con.cursor()

    where_clause = make_where_clause(pks)

    sql = "SELECT * FROM {} WHERE {}".format(tbl_name, where_clause)
    existing_rows = cur.execute(sql, row).fetchall()
    row = merge_rows(*existing_rows, row)

    keys = row.keys()
    col_names = ", ".join(keys)
    value_names = ", ".join(":" + k for k in keys)
    insert_sql = "REPLACE INTO {} ({}) VALUES ({})".format(
        tbl_name, col_names, value_names
    )

    cur.execute(insert_sql, row)
    con.commit()


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
            if row[key]:
                new_row[key] = row[key]
    return new_row
