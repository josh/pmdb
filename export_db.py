import json
import os
import sqlite3
import sys

con = sqlite3.connect("file:" + sys.argv[1] + "?mode=ro", uri=True)
con.row_factory = sqlite3.Row

root = sys.argv[2]

index_names = os.environ["INDEXES"].split()

for result in con.execute("SELECT * FROM movies"):
    row = dict(result)

    for index_name in index_names:
        filename = "{}.json".format(result[index_name])
        filename = os.path.join(root, index_name, filename)

        with open(filename, "w") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
