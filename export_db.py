import json
import os
import sqlite3

con = sqlite3.connect("data.sqlite3")
con.row_factory = sqlite3.Row
indexes = os.environ["INDEXES"].split()

for row in con.execute("SELECT * FROM movies"):
    for name in indexes:
        filename = os.path.join("gh-pages", name, row[name] + ".json")
        with open(filename, "w") as f:
            json.dump(dict(row), f, indent=2)
            f.write("\n")
