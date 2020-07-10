from beets.library import Library
from constants import DEFAULT_PATH_FOR_JSON_FILE
import json
import sys
from constants import *

with open(SCANNER_TAGS_FILE) as json_file:
    TAGS_MODEL = json.load(json_file)


def prompt_tags(db_file, query):
    library = Library(db_file)
    for track in library.items(query=query):
        try:
            scan_version = int(float(track.scan_version))
        except Exception:
            scan_version = 0
        if scan_version < VERSION:
            _prompt_for_track(track, TAGS_MODEL)
            track.scan_version = VERSION
            track.store()

def _prompt_for_track(track, tags):
    print("\n====================== \n - Title: %s\n"
          "- Artist: %s\n"
          "- Album %s\n =================\n"
          % (track.title, track.artist, track.album))
    for tag, values in tags.items():
        if tag.startswith("_"):
            continue
        loop = True
        while loop:
            user_input = input("Tag %s ? Values: %s" % (tag, values))
            if user_input == "" or user_input is None:
                loop = False
            if user_input.lower() == "skip":
                return
            identified_value = _identify_value(user_input, values)
            if identified_value is not None:
                print(identified_value)
                loop = False
                setattr(track, tag, identified_value)

def _identify_value(user_input, values):
    if isinstance(values[0], int):
        try:
            parsed_input = int(user_input)
            if parsed_input in values:
                return parsed_input
        except Exception:
            return None
    else:
        values = [v.lower() for v in values]
        # TODO: Case sensitive, identified value should have the right case
        if user_input.lower() in values:
            return user_input
        compatible_values = [v for v in values
                             if _are_strings_compatible(user_input, v)]
        if len(compatible_values) == 1:
            return compatible_values[0]
        return None

def _are_strings_compatible(compressed, original):
    compressed = compressed.lower()
    original = original.lower()
    if len(compressed) <= 0:
        return True
    if len(original) <= 0:
        return False
    s = compressed[0]
    try:
        index = original.index(s)
        return _are_strings_compatible(compressed[1:], original[index+1:])
    except Exception:
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        query = None
    else:
        query = sys.argv[1]

    with open(DEFAULT_PATH_FOR_JSON_FILE) as json_file:
        config = json.load(json_file)

    beets_db = config.get("beetsLibrary")
    prompt_tags(beets_db, query)

