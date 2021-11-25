PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "items" (
  "wikidata" text,
  "imdb" text,
  "tmdb" integer,
  "title" text
);
INSERT INTO items VALUES('Q172241','tt0111161',278,'The Shawshank Redemption');
INSERT INTO items VALUES('Q47703','tt0068646',238,'The Godfather');
INSERT INTO items VALUES('Q732960','tt0780504',64690,'Drive');
INSERT INTO items VALUES('Q60834962','tt1160419',438631,'Dune');
CREATE UNIQUE INDEX wikidata ON "items" ("wikidata" ASC);
CREATE UNIQUE INDEX imdb ON "items" ("imdb" ASC);
CREATE UNIQUE INDEX tmdb ON "items" ("tmdb" ASC);
COMMIT;
