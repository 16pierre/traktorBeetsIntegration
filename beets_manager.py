from beets.library import Library
from typing import Dict, List
from pathlib import Path
from data import Track
import unicodedata


def get_tracks(db_file, tag_list: List[str]) -> Dict[str, Track]:
    result = dict()
    library = Library(db_file)
    tag_list = [tag for tag in tag_list if tag != "rating" and not tag.startswith("_")]
    for item in library.items():
        path = convert_attr_to_string(item.path).lower()
        tags = {tag: _get_attr_dont_throw(item, tag) for tag in tag_list}
        rating = _get_int_attr_dont_throw(item, "rating")
        if not(rating is not None and 0 <= rating <= 5):
            rating = None
        result[path] = Track(Path(path), tags, rating)

    return result


def write_tracks_rating_and_tags(db_file, tracks: Dict[str, Track]):
    library = Library(db_file)
    conflicting_tracks = []
    traktor_modification_count = 0
    for i in library.items():
        path = str(i.path, 'utf-8').lower()
        if path in tracks:

            if tracks.get(path).rating is not None:
                i.rating = tracks.get(path).rating

            conflicting_tags = []
            for tag_key, traktor_tag_value in tracks.get(path).tags.items():
                existing_tag_in_beets = _get_attr_dont_throw(i, tag_key)
                if existing_tag_in_beets is None or existing_tag_in_beets != traktor_tag_value:
                    traktor_modification_count += 1

                setattr(i, tag_key, traktor_tag_value)
                if existing_tag_in_beets is not None and existing_tag_in_beets != traktor_tag_value:
                    conflicting_tags.append((tag_key, existing_tag_in_beets, traktor_tag_value))
            if conflicting_tags:
                conflicting_tracks.append((path, conflicting_tags))

            i.store()

    if conflicting_tracks:
        for c in conflicting_tracks[:10]:
            print("Conflict in '%s':\n  Conflicting tags (tag_key, beet_tags, traktor_tags):\n\t%s" % (c[0], c[1]))
        print("==========================")
        print("Conflicting tags were overwritten in beets: Traktor tags have priority over beets")
        print("Total conflicting tracks: %s" % len(conflicting_tracks))
    print("New tags coming from Traktor: %s" % traktor_modification_count)


def _get_attr_dont_throw(obj, attribute):
    if hasattr(obj, attribute):
        return str(getattr(obj, attribute))
    return None


def _get_int_attr_dont_throw(obj, attribute):
    try:
        return int(float(str(getattr(obj, attribute))))
    except Exception:
        return None


def convert_attr_to_string(attribute):
    if attribute is None:
        return None
    result = str(attribute, 'utf-8')
    # result = result.encode('ascii')
    # result = result.decode("utf-8")
    result = unicodedata.normalize('NFKC', result)
    return result
