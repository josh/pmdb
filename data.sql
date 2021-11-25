PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS 'items' (
  'wikidata' text,
  'imdb' text,
  'tmdb' integer
);
INSERT INTO items VALUES('Q172241','tt0111161',NULL);
INSERT INTO items VALUES('Q47703','tt0068646',NULL);
INSERT INTO items VALUES('Q732960','tt0780504',NULL);
INSERT INTO items VALUES('Q60834962','tt1160419',438631);
CREATE UNIQUE INDEX tmdb ON 'items' ('tmdb' ASC);
CREATE UNIQUE INDEX imdb ON 'items' ('imdb' ASC);
CREATE UNIQUE INDEX wikidata ON 'items' ('wikidata' ASC);
COMMIT;
