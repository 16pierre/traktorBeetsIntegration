from typing import Dict, List, Iterable
from data import Track, Playlist
from pathlib import Path
import os
import re
import traktor

_RECORDING_PATTERN = re.compile("\d{4}-\d{2}-\d{1,2}(_\d{1,2}h\d{2}m\d{2})?(_\d{1,2}h\d{2}m\d{2})?\.wav")


def remove_links_when_imported_in_beets_and_update_traktor_paths(
        traktor_nml_path: str,
        traktor_tracks: Dict[str, Track],
        beets_tracks: Dict[str, Track]
):
    tracks_symlinked_count = 0
    symlinks_removed_count = 0
    relocations = {}
    for beet_track in beets_tracks.values():
        symlinks = []
        last_symlink = beet_track.path
        while last_symlink.is_symlink():
            symlinks.append(last_symlink)
            last_symlink = Path(os.readlink(str(last_symlink)))

        if not symlinks:
            continue

        if last_symlink in [t.path for t in traktor_tracks.values()]:
            tracks_symlinked_count += 1
            print("Symlink target %s found in Traktor ! Paths: %s" % (last_symlink, symlinks))
            for l in symlinks:
                l.unlink()
                symlinks_removed_count += 1
            os.rename(str(last_symlink), str(symlinks[0]))
            relocations[last_symlink] = symlinks[0]
            _cleanup_empty_directories([last_symlink] + symlinks)

    print("Total number of symlinked tracks: %s ; removed links: %s" % (tracks_symlinked_count, symlinks_removed_count))

    print("Relocating tracks in Traktor...")
    traktor.update_tracks_locations(traktor_nml_path, relocations)


def _cleanup_empty_directories(original_paths: Iterable[Path]):
    directories_to_cleanup = set([p.parent for p in original_paths])
    next_cleanup = set()
    for d in directories_to_cleanup:
        if d.is_dir() and not os.listdir(str(d)):
            os.rmdir(str(d))
            next_cleanup.add(d.parent)
            print("Cleaned up empty dir %s" % d)
    _cleanup_empty_directories(next_cleanup)


def create_links_to_files_imported_in_traktor_but_not_in_beets(
        symlink_directory: Path,
        traktor_tracks: Dict[str, Track],
        beets_tracks: Dict[str, Track]):
    symlink_directory.mkdir(parents=True, exist_ok=True)
    not_in_beets = {p: t for p, t in traktor_tracks.items() if p not in beets_tracks}
    for t in not_in_beets.values():
        _create_temporary_symlink_path_for_track(symlink_directory, t)


def _get_temporary_symlink_path_for_track(
        symlink_directory: Path,
        track: Track) -> Path:
    if track.album is not None:
        symlink_directory = symlink_directory.joinpath(track.album)
    symlink_path = symlink_directory.joinpath(track.path.name)
    return symlink_path


def _create_temporary_symlink_path_for_track(
        symlink_directory: Path,
        track: Track):

    if bool(_RECORDING_PATTERN.match(track.path.name)):
        return
    if "Native Instruments" in str(track.path):
        return
    if "Traktor" in str(track.path):
        return

    symlink_path = _get_temporary_symlink_path_for_track(symlink_directory, track)
    symlink_path.parent.mkdir(parents=True, exist_ok=True)
    if symlink_path.exists() or symlink_path.is_symlink():
        return
    symlink_path.symlink_to(track.path)
    return


if __name__ == "__main__":
    assert bool(_RECORDING_PATTERN.match("2020-07-11_2h12m15.wav"))
    assert bool(_RECORDING_PATTERN.match("2020-08-01_21h12m27_00h57m46.wav"))

