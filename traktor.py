from traktor_nml_utils import TraktorCollection
import traktor_nml_utils.models.collection as TraktorModels
from typing import Type, List
from data import Playlist
from pathlib import Path


def path_to_traktor_formatted_path(path : Path, volume):
    if path is None or path.parent == path:
        return volume
    return path_to_traktor_formatted_path(path.parent, volume) + "/:" + path.name


def traktor_path_to_pathlib_path(traktor_dir, traktor_name) -> Path:
    return Path(traktor_dir.replace("/:", "/")).joinpath(traktor_name)


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


def create_playlist_directory(node : TraktorModels.Nodetype, name : str) -> TraktorModels.Nodetype:
    created_node = TraktorModels.Nodetype(type="FOLDER", name=name)
    created_node.subnodes = create_subnodes()
    node.subnodes.node.append(created_node)
    return created_node


def create_playlist(node: TraktorModels.Nodetype, name: str, volume: str, tracks: List[Path]) -> TraktorModels.Nodetype:
    created_playlist = TraktorModels.Nodetype(
        type="PLAYLIST",
        name=name,
        playlist=TraktorModels.Playlisttype(
            type="LIST",
            entry=[TraktorModels.Entrytype(
                primarykey=TraktorModels.Primarykeytype(
                    type="TRACK",
                    key=path_to_traktor_formatted_path(t, volume)
                ))
                for t in tracks]
        )
    )
    node.subnodes.node.append(created_playlist)
    return created_playlist


def write_auto_generated_playlists_to_traktor(
        collection_nml_path: str,
        playlists: List[Playlist],
        volume: str,
        folder_name: str):
    collection = TraktorCollection(Path(collection_nml_path))
    init_playlists_root_node(collection)
    delete_playlist_node(collection, folder_name)
    auto_generated_playlists_directory = create_playlist_directory(collection.nml.playlists.node, folder_name)
    for p in playlists:
        create_playlist(auto_generated_playlists_directory, p.name, volume, [Path(t) for t in p.tracks])

    collection.save()


def write_rating_to_traktor_collection(
        collection_nml,
        path_to_rating_dict
):
    collection = TraktorCollection(Path(collection_nml))
    for t in collection.nml.collection.entry:
        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file))

        # print(":".join("{:02x}".format(ord(c)) for c in path))

        if path in path_to_rating_dict:
            t.info.ranking = 51 * path_to_rating_dict[path]
            if t.info.ranking == 0:
                t.info.ranking = 51

    _save_collection(collection)


def write_comments_to_traktor_collection(
        collection_nml,
        path_to_tags_dict,
        tags_list
):
    collection = TraktorCollection(Path(collection_nml))
    for t in collection.nml.collection.entry:
        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file))

        if path in path_to_tags_dict:
            t.comment = _tags_to_comment(path_to_tags_dict[path], tags_list)

    _save_collection(collection)


def _tags_to_comment(track_tags, tags_list):
    result = ""
    for tag in tags_list:
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


def get_paths_to_rating_dict(
        collection_nml,
        volume
):
    result = dict()
    collection = TraktorCollection(Path(collection_nml))
    for t in collection.nml.collection.entry:
        if t.location.volume != volume:
            continue
        if not t.info.ranking:
            continue
        path = str(traktor_path_to_pathlib_path(t.location.dir, t.location.file))
        result[path] = t.info.ranking / 51
    return result

