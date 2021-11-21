import json
import os
import shutil
import sqlite3
import sys

con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row

with open("data.sql", "r") as f:
    con.executescript(f.read())

index_names = set()

for result in con.execute("PRAGMA index_list('movies')"):
    if result["unique"] == 1:
        index_names.add(result["name"])

index_info = {}

print("=== Loading indexes", file=sys.stderr)

for name in index_names:
    results = con.execute("PRAGMA index_info('" + name + "')")
    cols = index_info[name] = [result["name"] for result in results]
    print("{}: {}".format(name, ",".join(cols)))

for name in index_names:
    shutil.rmtree(name, ignore_errors=True)
    os.makedirs(name)

print("=== Dumping JSON rows", file=sys.stderr)

for result in con.execute("SELECT * FROM movies"):
    row = dict(result)

    for index_name in index_info:
        index_col_name = index_info[index_name][0]
        filename = "{}/{}.json".format(index_name, result[index_col_name])

        print(filename, file=sys.stderr)
        with open(filename, "w") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
