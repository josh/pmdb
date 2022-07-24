CREATE TABLE items (
  wikidata_qid text CHECK (wikidata_qid GLOB "Q*"),
  imdb_id text CHECK (imdb_id GLOB "tt*"),
  tmdb_type text CHECK (tmdb_type IN ("movie", "tv")),
  tmdb_id integer CHECK (tmdb_id IS NULL OR tmdb_type IS NOT NULL),
  trakt_type text CHECK (trakt_type IN ("movie", "show")),
  trakt_id integer CHECK (trakt_id IS NULL OR trakt_type IS NOT NULL),
  plex_type text CHECK (plex_type IN ("movie", "show")),
  plex_id text CHECK (plex_id IS NULL OR plex_type IS NOT NULL),
  appletv_id text CHECK (appletv_id GLOB "umc.cmc.*"),
  rottentomatoes_id text CHECK (rottentomatoes_id GLOB "m/*" OR rottentomatoes_id GLOB "tv/*"),
  title text,
  year integer CHECK (year >= 1900 AND year < 2050),
  director_qid text CHECK (wikidata_qid GLOB "Q*"),
  director text,
  duration integer CHECK (duration >= 0),
  tomatometer integer CHECK (tomatometer >= 0 AND tomatometer <= 100),
  CHECK (wikidata_qid IS NOT NULL OR imdb_id IS NOT NULL OR tmdb_id IS NOT NULL)
);
CREATE UNIQUE INDEX plex ON "items" ("plex_type", "plex_id");
CREATE UNIQUE INDEX trakt ON "items" ("trakt_type", "trakt_id");
CREATE UNIQUE INDEX tmdb ON "items" ("tmdb_type", "tmdb_id");
CREATE UNIQUE INDEX imdb ON "items" ("imdb_id");
CREATE UNIQUE INDEX wikidata ON "items" ("wikidata_qid");
CREATE INDEX director ON "items" ("director_qid");
