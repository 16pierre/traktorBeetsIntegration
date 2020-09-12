from typing import Dict, List
from pathlib import Path


class Track:
    def __init__(self, path: Path, tags: Dict[str, str], rating: int, album: str = None, comment: str = None):
        self.path = path
        self.tags = tags
        self.rating = rating
        self.album = album
        self.comment = comment

    def __str__(self):
        return "PATH: %s ; TAGS: %s ; RATING: %s" % (self.path, self.tags, self.rating)


class Playlist:
    def __init__(self, name, tracks: List[Track], tag_keys: List[str] = [], folder_index: int = 0):
        self.name = name
        self.tracks = tracks
        self.tag_keys = tag_keys
        self.folder_index = folder_index

    def contains_track(self, track_path: Path):
        for t in self.tracks:
            if t.path == track_path:
                return True
        return False


class TagsConfiguration:
    def __init__(self, tag_models: Dict[str, List[str]], playlists_to_generate: List[List[str]]):
        self.tag_models = tag_models
        self.playlists_to_generate = playlists_to_generate

    @staticmethod
    def from_dict(json_dict: Dict):
        playlists_to_generate = json_dict.pop("_playlists")
        tag_models = {k: v for k, v in json_dict.items()}
        return TagsConfiguration(tag_models, playlists_to_generate)
