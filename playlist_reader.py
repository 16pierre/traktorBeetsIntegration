from pathlib import Path
from data import Playlist
import os


def _list_m3u_at_path(playlist_folder):
    for root, _, files in os.walk(playlist_folder):
        for f in files:
            if f.endswith("m3u"):
                yield Path(root).joinpath(f)


def _m3u_to_playlist(m3u_path : Path):
    tracks = []
    with open(str(m3u_path.resolve()), "rt") as fout:
        for track in fout:
            tracks.append(track.strip())

    return Playlist(m3u_path.name[:-4], tracks)


def list_playlists_at_path(playlist_folder):
    return [_m3u_to_playlist(f) for f in _list_m3u_at_path(playlist_folder)
            if _m3u_to_playlist(f).tracks]

