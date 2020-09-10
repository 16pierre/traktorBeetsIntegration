from typing import Dict, List
from pathlib import Path


class Track:
    def __init__(self, path: Path, tags: Dict[str, str], rating: int):
        self.path = path
        self.tags = tags
        self.rating = rating

    def __str__(self):
        return "PATH: %s ; TAGS: %s ; RATING: %s" % (self.path, self.tags, self.rating)


class Playlist:
    def __init__(self, name, tracks: List[Track]):
        self.name = name
        self.tracks = tracks

