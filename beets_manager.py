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
        path = convert_attr_to_string(item.path)
        tags = {tag: _get_attr_dont_throw(item, tag) for tag in tag_list}
        rating = _get_int_attr_dont_throw(item, "rating")
        if not(rating is not None and 0 <= rating <= 5):
            rating = None
        result[path] = Track(Path(path), tags, rating)

    return result


def write_ratings(db_file, tracks: Dict[str, Track]):
    library = Library(db_file)
    for i in library.items():
        path = str(i.path, 'utf-8')
        if path in tracks and tracks.get(path).rating is not None:
            i.rating = tracks.get(path).rating
            i.store()


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
