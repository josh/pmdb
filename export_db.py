import json
import os
import shutil
import sqlite3
import sys

assert len(sys.argv) == 3


con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row

with open(sys.argv[1], "r") as f:
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

print("=== Dumping JSON rows", file=sys.stderr)

root = sys.argv[2]

for name in index_names:
    dirname = os.path.join(root, name)
    shutil.rmtree(dirname, ignore_errors=True)
    os.makedirs(dirname)

for result in con.execute("SELECT * FROM movies"):
    row = dict(result)

    for index_name in index_info:
        index_col_name = index_info[index_name][0]
        filename = "{}.json".format(result[index_col_name])
        filename = os.path.join(root, index_name, filename)

        print(filename, file=sys.stderr)
        with open(filename, "w") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
