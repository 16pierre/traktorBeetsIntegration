from beets.library import Library
from constants import DEFAULT_PATH_FOR_JSON_FILE
import json
import sys
import utils
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
            identified_value = utils.identify_value(user_input, values)
            if identified_value is not None:
                print(identified_value)
                loop = False
                setattr(track, tag, identified_value)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        query = None
    else:
        query = sys.argv[1]

    print('Query: "%s"' % query)

    with open(DEFAULT_PATH_FOR_JSON_FILE) as json_file:
        config = json.load(json_file)

    beets_db = config.get("beetsLibrary")
    prompt_tags(beets_db, query)

