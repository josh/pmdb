import argparse
import logging
import sqlite3


def main():
    parser = argparse.ArgumentParser(
        description="Reinsert SQLite database table rows.",
    )
    parser.add_argument("--database", action="store")
    parser.add_argument("--table", action="store")
    parser.add_argument("--order-by", action="store")
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

    tbl_name = args.table
    assert tbl_name

    order_by = args.order_by
    assert order_by

    sql = "SELECT * FROM {} ORDER BY {}".format(tbl_name, order_by)
    rows = con.execute(sql).fetchall()

    con.execute("DELETE FROM {}".format(tbl_name))

    for row in rows:
        keys = row.keys()
        col_names = ", ".join(keys)
        value_names = ", ".join(":" + k for k in keys)
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
            tbl_name,
            col_names,
            value_names,
        )
        con.execute(sql, row)

    con.commit()


if __name__ == "__main__":
    main()
