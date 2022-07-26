import argparse
import logging
import os
import sqlite3

import requests

from db import items_upsert

trakt_list_endpoints = {
    "/users/joshpeek/collection/movies",
    "/users/joshpeek/collection/shows",
    "/users/joshpeek/ratings",
    "/users/joshpeek/watched/movies",
    "/users/joshpeek/watched/shows",
    "/users/joshpeek/watchlist",
    "/users/justin/lists/2142753/items",
    "/users/justin/lists/2143363/items",
}

trakt_people_endpoints = {
    "/people/aaron-sorkin/movies",
    "/people/alejandro-gonzalez-inarritu/movies",
    "/people/alex-garland/movies",
    "/people/alex-kurtzman/movies",
    "/people/alfonso-cuaron/movies",
    "/people/barry-levinson/movies",
    "/people/ben-stiller/movies",
    "/people/brad-bird/movies",
    "/people/brad-pitt/movies",
    "/people/brian-de-palma/movies",
    "/people/bryan-singer/movies",
    "/people/cameron-crowe/movies",
    "/people/cary-joji-fukunaga/movies",
    "/people/christopher-mcquarrie/movies",
    "/people/christopher-nolan/movies",
    "/people/damien-chazelle/movies",
    "/people/dan-gilroy/movies",
    "/people/daniel-craig/movies",
    "/people/danny-boyle/movies",
    "/people/darren-aronofsky/movies",
    "/people/david-cronenberg/movies",
    "/people/david-fincher/movies",
    "/people/david-lynch/movies",
    "/people/david-o-russell/movies",
    "/people/denis-villeneuve/movies",
    "/people/doug-liman/movies",
    "/people/edward-zwick/movies",
    "/people/ethan-coen/movies",
    "/people/francis-ford-coppola/movies",
    "/people/j-j-abrams/movies",
    "/people/james-cameron/movies",
    "/people/james-mangold/movies",
    "/people/jason-reitman/movies",
    "/people/jeremy-saulnier/movies",
    "/people/joel-coen/movies",
    "/people/joel-edgerton/movies",
    "/people/john-woo/movies",
    "/people/joseph-kosinski/movies",
    "/people/kathryn-bigelow/movies",
    "/people/martin-scorsese/movies",
    "/people/michael-mann/movies",
    "/people/neil-jordan/movies",
    "/people/oliver-stone/movies",
    "/people/paul-thomas-anderson/movies",
    "/people/quentin-tarantino/movies",
    "/people/ridley-scott/movies",
    "/people/rob-reiner/movies",
    "/people/robert-redford/movies",
    "/people/robert-towne/movies",
    "/people/ron-howard/movies",
    "/people/s-craig-zahler/movies",
    "/people/shane-black/movies",
    "/people/stanley-kubrick/movies",
    "/people/steven-soderbergh/movies",
    "/people/steven-spielberg/movies",
    "/people/sydney-pollack/movies",
    "/people/terrence-malick/movies",
    "/people/tom-cruise/movies",
    "/people/tony-gilroy/movies",
    "/people/tony-scott/movies",
    "/people/wes-anderson/movies",
    "/people/yorgos-lanthimos/movies",
}


def main():
    parser = argparse.ArgumentParser(
        description="Discover new items via Trakt.",
    )
    parser.add_argument("--database", action="store")
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

    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row

    discover_trakt_lists(con)
    discover_trakt_people(con)


def discover_trakt_lists(con):
    for endpoint in trakt_list_endpoints:
        for item in trakt_paginated_request(endpoint):
            row = extract_row(item)
            if row:
                items_upsert(con, row, overwrite=False)


def discover_trakt_people(con):
    for endpoint in trakt_people_endpoints:
        credits = trakt_request(endpoint)

        for credit in credits["cast"]:
            if is_playing_character(credit["character"]):
                row = extract_row(credit)
                if row:
                    items_upsert(con, row, overwrite=False)

        for credit in credits["crew"].get("directing", []):
            row = extract_row(credit)
            if row:
                items_upsert(con, row, overwrite=False)


def is_playing_character(character):
    character = character.lower()
    if character == "":
        return False
    if character.startswith("self"):
        return False
    if character.startswith("himself") or character.startswith("herself"):
        return False
    if "uncredited" in character:
        return False
    if character.startswith("(") and character.endswith(")"):
        return False
    return True


def trakt_request(endpoint):
    url = "https://api.trakt.tv" + endpoint
    headers = {
        "Content-Type": "application/json",
        "trakt-api-key": os.environ["TRAKT_CLIENT_ID"],
        "trakt-api-version": "2",
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()


def trakt_paginated_request(endpoint):
    url = "https://api.trakt.tv" + endpoint
    headers = {
        "Content-Type": "application/json",
        "trakt-api-key": os.environ["TRAKT_CLIENT_ID"],
        "trakt-api-version": "2",
    }
    page = 1
    page_count = 1

    while True:
        params = {"page": page, "limit": 1000}
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()

        page = int(r.headers.get("X-Pagination-Page", 1))
        page_count = int(r.headers.get("X-Pagination-Page-Count", 1))

        items = r.json()
        assert type(items) == list
        yield from items

        if page < page_count:
            page += 1
            continue
        else:
            break


def extract_row(item):
    row = {}

    if "movie" in item:
        row["title"] = item["movie"]["title"]
        ids = item["movie"]["ids"]
        row["trakt_type"] = "movie"
        row["trakt_id"] = ids["trakt"]
        if "imdb" in ids:
            row["imdb_id"] = ids["imdb"]
        if "tmdb" in ids:
            row["tmdb_type"] = "movie"
            row["tmdb_id"] = ids["tmdb"]

    if "show" in item:
        row["title"] = item["show"]["title"]
        ids = item["show"]["ids"]
        row["trakt_type"] = "show"
        row["trakt_id"] = ids["trakt"]
        if "imdb" in ids:
            row["imdb_id"] = ids["imdb"]
        if "tmdb" in ids:
            row["tmdb_type"] = "tv"
            row["tmdb_id"] = ids["tmdb"]

    if row["imdb_id"] is None:
        return None

    return row


if __name__ == "__main__":
    main()
