import argparse
import logging
import sqlite3


def main():
    parser = argparse.ArgumentParser(
        description="Clean up bad database items.",
    )
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

    # clean_missing_imdb(con)


# def clean_missing_imdb(con):
#     con.execute("DELETE FROM items WHERE imdb_id IS NULL")
#     con.commit()


if __name__ == "__main__":
    main()
