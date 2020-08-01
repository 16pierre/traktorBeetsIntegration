from traktor_nml_utils import TraktorCollection
import uuid
from data import Playlist
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_collection(nml_path):
    return ET.parse(nml_path)

def playlist_root(et_root):
    return list(et_root.findall("PLAYLISTS"))[0]

def remove_custom_playlist_folder(playlist_root, folder_name):
    for entry in playlist_root.findall("NODE"):
        if entry is not None and entry.get("NAME") == folder_name:
            print("Removing existing folder")
            playlist_root.remove(entry)

def fresh_playlist_node(folder_name, playlists, volume):

    """

<PLAYLISTS>
    <NODE TYPE="FOLDER" NAME="$ROOT">
    <SUBNODES COUNT="41">
    <NODE TYPE="PLAYLIST" NAME="aaa roger">
    <PLAYLIST ENTRIES="14" TYPE="LIST" UUID="023e5cc077aa4fe2b4efd5d32c58079c"><ENTRY>
    <PRIMARYKEY TYPE="TRACK" KEY="Macintosh HD/:Users/:16pierre/:Music/:iTunes/:iTunes Media/:Music/:Beyond the Shadow of a Dream.mp3">
    </PRIMARYKEY>
</ENTRY>
    """
    folder = ET.Element("NODE")
    folder.set("TYPE", "FOLDER")
    folder.set("NAME", folder_name)

    subnodes = ET.Element("SUBNODES")

    for p in playlists:
        playlist_node = ET.Element("NODE")
        playlist_node.set("NAME", p.name)
        playlist_node.set("TYPE", "PLAYLIST")

        playlist = ET.Element("PLAYLIST")
        playlist.set("TYPE", "LIST")
        playlist.set("ENTRIES", str(len(p.tracks)))
        playlist.set("UUID", str(uuid.uuid4()))

        for t in reversed(p.tracks):
            entry = ET.Element("ENTRY")
            track = ET.Element("PRIMARYKEY")
            track.set("TYPE", "TRACK")
            track.set("KEY", path_to_traktor_formatted_path(Path(t), volume))
            entry.insert(0, track)
            playlist.insert(0, entry)

        playlist_node.insert(0, playlist)
        subnodes.insert(0, playlist_node)

    folder.insert(0, subnodes)
    return folder

def path_to_traktor_formatted_path(path : Path, volume):
    if path is None or path.parent == path:
        return volume
    return path_to_traktor_formatted_path(path.parent, volume) + "/:" + path.name

def traktor_path_to_pathlib_path(traktor_dir, traktor_name) -> Path:
    return Path(traktor_dir.replace("/:", "/")).joinpath(traktor_name)

def create_or_replace_custom_playlists(playlist_root, folder_name, playlists, volume):
    remove_custom_playlist_folder(playlist_root, folder_name)
    playlist_root.insert(0, fresh_playlist_node(folder_name, playlists, volume))

def write_custom_playlists_to_traktor_collection(
        collection_nml,
        playlists,
        volume,
        folder_name
):
    collection = parse_collection(collection_nml)
    create_or_replace_custom_playlists(playlist_root(collection.getroot()),
                                       folder_name,
                                       playlists,
                                       volume)
    collection.write(collection_nml)

def write_rating_to_traktor_collection(
        collection_nml,
        path_to_rating_dict
):
    collection = TraktorCollection(collection_nml)
    for t in collection.entries:
        path = str(traktor_path_to_pathlib_path(t.dir, t.file))

        # print(":".join("{:02x}".format(ord(c)) for c in path))

        if path in path_to_rating_dict:
            t.ranking = 51 * path_to_rating_dict[path]
            if t.ranking == 0:
                t.ranking = 51
            t.save()

def write_comments_to_traktor_collection(
        collection_nml,
        path_to_tags_dict,
        tags_list
):
    collection = TraktorCollection(collection_nml)
    for t in collection.entries:
        path = str(traktor_path_to_pathlib_path(t.dir, t.file))

        if path in path_to_tags_dict:
            t.comment = _tags_to_comment(path_to_tags_dict[path], tags_list)
            t.save()

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

def get_paths_to_rating_dict(
        collection_nml
):
    result = dict()
    collection = TraktorCollection(collection_nml)
    for t in collection.entries:
        if not t.ranking:
            continue
        path = str(traktor_path_to_pathlib_path(t.dir, t.file))
        result[path] = t.ranking / 51
    return result

