from traktor_nml_utils import TraktorCollection
import traktor_nml_utils.models.collection as TraktorModels
from auto_generated_playlist import AutoGeneratedPlaylistManager
from typing import List, Dict
from data import Playlist, Track
from pathlib import Path


def path_to_traktor_formatted_path(path : Path, volume):
    if path is None or path.parent == path:
        return volume
    return path_to_traktor_formatted_path(path.parent, volume) + "/:" + path.name


def traktor_path_to_pathlib_path(traktor_dir: str, traktor_name: str) -> Path:
    return Path(traktor_dir.replace("/:", "/")).joinpath(traktor_name)


def pathlib_path_to_traktor_dir_and_file_couple(path: Path):
    return (str(path.parent.absolute()) + "/").replace("/", "/:"), str(path.name)


def traktor_absolute_path_to_pathlib_path(traktor_absolute_path: str) -> Path:
    return Path(("/" + traktor_absolute_path.split("/:", 1)[1]).replace("/:", "/"))


def pathlib_path_to_traktor_absolute_path(path: Path, volume: str) -> str:
    return volume + str(path).replace("/", "/:")


def init_playlists_root_node(traktor_collection : TraktorCollection):
    if not traktor_collection.nml.playlists:
        traktor_collection.nml.playlists = TraktorModels.Playliststype()
    if not traktor_collection.nml.playlists.node:
        traktor_collection.nml.playlists.node = TraktorModels.Nodetype(
            type="FOLDER", name="$ROOT")
    if not traktor_collection.nml.playlists.node.subnodes:
        traktor_collection.nml.playlists.node.subnodes = TraktorModels.Subnodestype()
    if not traktor_collection.nml.playlists.node.subnodes.node:
        traktor_collection.nml.playlists.node.subnodes.node = []


def create_subnodes():
    subnodes = TraktorModels.Subnodestype()
    subnodes.node = []
    return subnodes


def delete_playlist_node(traktor_collection : TraktorCollection, name : str):
    index_to_delete = -1
    for i, subnode in enumerate(traktor_collection.nml.playlists.node.subnodes.node):
        if subnode.name == name:
            index_to_delete = i
            break
    if index_to_delete >= 0:
        traktor_collection.nml.playlists.node.subnodes.node.pop(index_to_delete)


def list_playlists_in_node(node: TraktorModels.Nodetype) -> List[Playlist]:
    result = []
    if node.playlist and node.playlist.entry:
        tracks = []
        for entry in node.playlist.entry:
            if not entry.primarykey or entry.primarykey.type != "TRACK":
                continue
            track_path = Path(str(traktor_absolute_path_to_pathlib_path(entry.primarykey.key)).lower())
            tracks.append(Track(track_path, dict(), None))
        result.append(Playlist(node.name, tracks))

    if node.subnodes and node.subnodes.node:
        for n in node.subnodes.node:
            result.extend(list_playlists_in_node(n))

    return result


def list_playlists_in_collection(traktor_collection: TraktorCollection, playlist_folder_name: str) -> List[Playlist]:
    if not traktor_collection.nml.playlists or not traktor_collection.nml.playlists.node:
        return []
    for node in traktor_collection.nml.playlists.node.subnodes.node:
        if  node.name == playlist_folder_name:
            result = list_playlists_in_node(node)
            print("Found %s Traktor playlists in folder %s" % (len(result), playlist_folder_name))
            return result

    print("Traktor warning: playlist folder %s not found !" % playlist_folder_name)
    return []


def create_playlist_directory(node : TraktorModels.Nodetype, name : str) -> TraktorModels.Nodetype:
    if node.subnodes and node.subnodes.node:
        for n in node.subnodes.node:
            if n.name == name:
                return n
    created_node = TraktorModels.Nodetype(type="FOLDER", name=name)
    created_node.subnodes = create_subnodes()
    node.subnodes.node.append(created_node)
    return created_node


def create_playlist(node: TraktorModels.Nodetype, name: str, volume: str, tracks: List[Track]) -> TraktorModels.Nodetype:
    created_playlist = TraktorModels.Nodetype(
        type="PLAYLIST",
        name=name,
        playlist=TraktorModels.Playlisttype(
            type="LIST",
            entry=[TraktorModels.Entrytype(
                primarykey=TraktorModels.Primarykeytype(
                    type="TRACK",
                    key=path_to_traktor_formatted_path(t.path, volume)
                ))
                for t in tracks]
        )
    )
    node.subnodes.node.append(created_playlist)
    return created_playlist


def write_playlists_to_traktor(
        collection_nml_path: str,
        playlists: List[Playlist],
        volume: str,
        folder_name: str):
    collection = TraktorCollection(Path(collection_nml_path))
    init_playlists_root_node(collection)
    delete_playlist_node(collection, folder_name)
    auto_generated_playlists_node = create_playlist_directory(collection.nml.playlists.node, folder_name)
    for p in playlists:
        directory_for_playlist = auto_generated_playlists_node
        if p.tag_keys and p.folder_index:
            subnode_name_prefix = "%02d" % p.folder_index
            subnode_name = subnode_name_prefix + " - " + ", ".join(p.tag_keys)
            directory_for_playlist = create_playlist_directory(auto_generated_playlists_node, subnode_name)

        create_playlist(directory_for_playlist, p.name, volume, p.tracks)

    collection.save()


def write_rating_to_traktor_collection(
        collection_nml: str,
        tracks: Dict[str, Track]):
    collection = TraktorCollection(Path(collection_nml))
    for t in collection.nml.collection.entry:
        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file)).lower()

        # print(":".join("{:02x}".format(ord(c)) for c in path))

        if path in tracks and tracks[path].rating is not None:
            t.info.ranking = 51 * tracks[path].rating
            if t.info.ranking == 0:
                t.info.ranking = 51

    _save_collection(collection)


def write_comments_to_traktor_collection(
        collection_nml: str,
        tracks: Dict[str, Track],
        tags_list: List[str]):
    collection = TraktorCollection(Path(collection_nml))
    for t in collection.nml.collection.entry:
        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file)).lower()

        if path in tracks:
            t.info.comment = _tags_to_comment(tracks[path].tags, tags_list)

    _save_collection(collection)


def _tags_to_comment(track_tags, tags_list):
    result = ""
    for tag in reversed(tags_list):
        tag_value = track_tags.get(tag)
        if tag_value is not None and tag_value != "":
            if tag_value == "yes":
                result += "%s - " % tag
            # elif tag_value == "no":
            #     result += "!%s - " % tag
            else:
                try:
                    to_int = int(float(tag_value))
                    result += "%s: %d -" % (tag, to_int)
                except Exception:
                    result += "%s - " % tag_value
    if len(result) >= 2:
        return result[:-2]
    return ""


def _save_collection(collection_obj):
    collection_obj.save()


def list_auto_generated_playlists(
        collection_nml: str,
        auto_generated_playlists_folder: str) -> List[Playlist]:
    collection = TraktorCollection(Path(collection_nml))
    return list_playlists_in_collection(collection, auto_generated_playlists_folder)


def get_tracks(
        collection_nml: str,
        volume: str,
        auto_generated_playlists_folder: str,
        playlist_manager: AutoGeneratedPlaylistManager) -> Dict[str, Track]:
    result = dict()
    collection = TraktorCollection(Path(collection_nml))

    auto_generated_playlists = list_playlists_in_collection(collection, auto_generated_playlists_folder)

    tagged_tracks_not_flattened = playlist_manager.tagged_tracks_from_playlists(auto_generated_playlists)

    for t in collection.nml.collection.entry:
        if t.location.volume != volume:
            continue

        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file)).lower()
        tags = dict()
        comment = None
        if t.info and t.info.comment:
            comment = t.info.comment
        if path in tagged_tracks_not_flattened:
            for tagged_track in tagged_tracks_not_flattened[path]:
                for tag_key, tag_value in tagged_track.tags.items():
                    if tag_key not in tags:
                        tags[tag_key] = tag_value
                    elif tags[tag_key] != tag_value:
                        # Conflict between playlists, this means the user has placed the track in multiple playlists
                        # To see which tags are the previous/new values, let's check the comment
                        if tags[tag_key] in comment and \
                                (tag_value not in comment or len(tag_value) < len(tags[tag_key])):
                            tags[tag_key] = tag_value

        track = Track(path=Path(path), tags=tags, rating=None, comment=comment)
        if t.info.ranking is not None and int(t.info.ranking) >= 51:
            track.rating = t.info.ranking / 51
        if t.album is not None and t.album.title:
            track.album = t.album.title
        result[path] = track
    return result


def update_tracks_locations(
        collection_nml: str,
        old_to_new_locations: Dict[Path, Path],
        volume: str):

    collection = TraktorCollection(Path(collection_nml))
    count = 0
    for t in collection.nml.collection.entry:
        path = Path(str(traktor_path_to_pathlib_path(t.location.dir, t.location.file)).lower())
        if path in old_to_new_locations:
            new_path = old_to_new_locations[path]
            t.location.dir, t.location.file = pathlib_path_to_traktor_dir_and_file_couple(new_path)
            count += 1
            print("TRAKTOR: Replaced %s by %s" % (path, new_path))

    if collection.nml.playlists and collection.nml.playlists.node.subnodes:
        for subnode in collection.nml.playlists.node.subnodes.node:
            if subnode.subnodes and subnode.subnodes.node:
                for playlist in subnode.subnodes.node:
                    if playlist.playlist and playlist.playlist.entry:
                        for t in playlist.playlist.entry:
                            if not t.primarykey or not t.primarykey.key:
                                continue
                            p = traktor_absolute_path_to_pathlib_path(t.primarykey.key)
                            if p in old_to_new_locations:
                                new_path = old_to_new_locations[path]
                                t.primarykey.key = pathlib_path_to_traktor_absolute_path(new_path, volume)
                                print("TRAKTOR PLAYLIST: Replaced %s by %s" % (path, new_path))

    _save_collection(collection)
    print("Relocated %s tracks in Traktor" % count)


if __name__ == "__main__":
    assert pathlib_path_to_traktor_dir_and_file_couple(
        traktor_path_to_pathlib_path("/:Users/:16pierre/:Music/:DJLibrary/:Disclosure/:Moog for Love/:",
                                        "02 Feel Like I Do.mp3")) == \
           ("/:Users/:16pierre/:Music/:DJLibrary/:Disclosure/:Moog for Love/:", "02 Feel Like I Do.mp3")
    pass

