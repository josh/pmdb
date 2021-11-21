import json
import os
import sqlite3
import sys

con = sqlite3.connect("file:" + sys.argv[1] + "?mode=ro", uri=True)
con.row_factory = sqlite3.Row

index_names = set()

for result in con.execute("PRAGMA index_list('movies')"):
    if result["unique"] == 1:
        index_names.add(result["name"])

index_info = {}

for name in index_names:
    results = con.execute("PRAGMA index_info('" + name + "')")
    cols = index_info[name] = [result["name"] for result in results]

root = sys.argv[2]

for result in con.execute("SELECT * FROM movies"):
    row = dict(result)

    for index_name in index_info:
        index_col_name = index_info[index_name][0]
        assert index_col_name == index_name
        filename = "{}.json".format(result[index_col_name])
        filename = os.path.join(root, index_name, filename)

        with open(filename, "w") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
