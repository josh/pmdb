PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "movies" (
  "wikidata" text,
  "imdb" text
);
INSERT INTO movies VALUES('Q47703','tt0068646');
INSERT INTO movies VALUES('Q172241','tt0111161');
CREATE UNIQUE INDEX wikidata ON "movies" ("wikidata" ASC);
CREATE UNIQUE INDEX imdb ON "movies" ("imdb" ASC);
COMMIT;
