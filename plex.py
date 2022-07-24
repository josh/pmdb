import os

from plexapi.myplex import MyPlexAccount

PLEX_ACCOUNT = None


def _connect():
    global PLEX_ACCOUNT
    if PLEX_ACCOUNT:
        return
    PLEX_ACCOUNT = MyPlexAccount(
        username=os.environ["PLEX_USERNAME"],
        password=os.environ["PLEX_PASSWORD"],
        token=os.environ["PLEX_TOKEN"],
    )


def parse_plex_guid(guid):
    assert isinstance(guid, str)
    assert guid.startswith("plex://")
    (_, _, type, id) = guid.split("/", 3)
    assert type == "movie" or type == "show"
    return (type, id)


def lookup_plex_guid(imdb_id, title):
    _connect()
    assert isinstance(imdb_id, str) and imdb_id.startswith("tt")
    assert isinstance(title, str)
    imdb_guid = "imdb://{}".format(imdb_id)
    for video in PLEX_ACCOUNT.searchDiscover(title, limit=5):
        video = PLEX_ACCOUNT.fetchItem(
            "https://metadata.provider.plex.tv{}".format(video.key)
        )
        for guid in video.guids:
            if guid.id == imdb_guid:
                return parse_plex_guid(video.guid)
    return None
