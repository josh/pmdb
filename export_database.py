import argparse
import json
import logging
import os
import shutil
import sqlite3


def main():
    parser = argparse.ArgumentParser(
        description="Export SQLite database to JSON files."
    )
    parser.add_argument("--database", action="store")
    parser.add_argument("--output", action="store")
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

    con = sqlite3.connect("file:{}?mode=ro".format(args.database), uri=True)
    con.row_factory = sqlite3.Row
    export(con, args.output)


def export(con, output_dir):
    clean_dir(output_dir)
    export_tables(con, output_dir)
    export_indexes(con, output_dir)


def export_tables(con, output_dir):
    for tbl_name in schema_tables(con):
        logging.info("Exporting table '{}'".format(tbl_name))

        sql = "SELECT * FROM {}".format(tbl_name)
        rows = [clean_dict(row) for row in con.execute(sql)]

        filename = os.path.join(output_dir, tbl_name + ".json")
        write_json(filename, rows)


def export_indexes(con, output_dir):
    for index_info in schema_indexes(con):
        export_index(con, output_dir, index_info)


def export_index(con, output_dir, index_info):
    index_name = index_info["name"]
    unique = index_info["unique"]

    logging.info("Exporting index '{}'".format(index_name))

    indexed_rows = {}
    filename_index_keys = {}

    sql = "SELECT * FROM {}".format(index_info["tbl_name"])
    for row in con.execute(sql):
        row = clean_dict(row)

        index_keys = []
        has_null_values = False
        for col in index_info["columns"]:
            if row[col] is None:
                has_null_values = True
            index_keys.append(str(row[col]))

        if unique and has_null_values:
            continue

        filename = os.path.join(output_dir, index_name, *index_keys) + ".json"
        filename_index_keys[filename] = index_keys
        insert_value(indexed_rows, index_keys, row, unique)

    for filename in filename_index_keys:
        value = get_value(indexed_rows, filename_index_keys[filename])
        write_json(filename, value)

    filename = os.path.join(output_dir, index_info["name"] + ".json")
    write_json(filename, indexed_rows)


def write_json(filename, obj):
    logging.debug("Writing '{}'".format(filename))

    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)

    with open(filename, "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def clean_dir(output_dir):
    if not os.path.exists(output_dir):
        return

    for name in os.listdir(output_dir):
        path = os.path.join(output_dir, name)
        if os.path.isdir(path) and not name.startswith("."):
            logging.debug("Removing '{}'".format(path))
            shutil.rmtree(path)
        elif os.path.isfile(path) and path.endswith(".json"):
            logging.debug("Removing '{}'".format(path))
            os.remove(path)


def schema_tables(con):
    sql = "SELECT name FROM sqlite_master WHERE type == 'table';"
    for row in con.execute(sql):
        yield row[0]


def schema_indexes(con):
    sql = "SELECT tbl_name, name FROM sqlite_master WHERE type == 'index';"
    for (tbl_name, name) in con.execute(sql):
        yield schema_index_info(con, tbl_name, name)


def schema_index_info(con, table_name, index_name):
    sql = "PRAGMA index_list('{}');".format(table_name)
    for row in con.execute(sql):
        if row["name"] == index_name:
            info = {
                "name": index_name,
                "tbl_name": table_name,
                "unique": row["unique"] == 1 or row["origin"] == "pk",
                "origin": row["origin"],
                "partial": row["partial"] == 1,
            }
    assert info

    info["columns"] = []
    sql = "PRAGMA index_info('{}');".format(index_name)
    for row in con.execute(sql):
        info["columns"].append(row["name"])

    return info


def insert_value(obj, keys, value, unique=False):
    keys = list(keys)
    last_key = keys.pop()

    root = obj
    assert type(root) is dict
    for key in keys:
        if key not in root:
            root[key] = {}
        root = root[key]
        assert type(root) is dict

    if unique:
        assert last_key not in root
        root[last_key] = value
    else:
        if last_key not in root:
            root[last_key] = []
        values = root[last_key]
        assert type(values) is list
        values.append(value)


def clean_dict(obj):
    return {k: v for k, v in dict(obj).items() if v is not None}


def get_value(obj, keys):
    value = obj
    for key in keys:
        assert type(value) is dict
        value = value[key]
    return value


if __name__ == "__main__":
    main()
