import json
import sys
from constants import *

with open(SCANNER_TAGS_FILE) as json_file:
    TAGS_MODEL = json.load(json_file)

# TODO: Don't re-write new smartPlaylist in YAML, this kills existing config

_FORMAT_NAME    = "    - name: %s.m3u\n"
_FORMAT_QUERY   = "      query: %s\n"


def _yield_name_and_queries(tags_info):
    query_types = tags_info["_playlists"]
    for i in range(len(query_types)):
        query_keys = query_types[i]
        for tags_to_values in _next_tags_to_values(tags_info, query_keys, dict(), 0):
            name = _playlist_name(tags_info, i, tags_to_values)
            yield name, _query(tags_to_values)


def _next_tags_to_values(
        tags_info,
        query_keys,
        current_dict,
        current_tag_index):

    if current_tag_index >= len(query_keys):
        yield current_dict.copy()
        return

    for current_value_index in range(len(tags_info[query_keys[current_tag_index]])):
        current_dict[query_keys[current_tag_index]] = \
            tags_info[query_keys[current_tag_index]][current_value_index]
        yield from _next_tags_to_values(
            tags_info,
            query_keys,
            current_dict.copy(),
            current_tag_index + 1)


def _playlist_name(tags_info, index, tags_to_values_dict):
    tags_initials = "".join([k[0] for k in tags_info["_playlists"][index]])
    return ("%02d_%s %s" % (index + 1, tags_initials, _query(tags_to_values_dict).replace(":", "="))).strip()


def _query(tags_to_values_dict):
    query = ""
    for k, v in tags_to_values_dict.items():
        query += "%s:'%s' " % (k, v)
    return query


if __name__ == "__main__":

    if len(sys.argv) < 2:
        config_path = DEFAULT_PATH_FOR_JSON_FILE
    else:
        config_path = sys.argv[1]

    with open(config_path) as json_file:
        config = json.load(json_file)

    beets_template = config['beetsConfigTemplate']
    beets_generated = config['beetsConfigGenerated']

    with open(beets_template, "rt") as fin:
        with open(beets_generated, "wt") as fout:
            for line in fin:
                if MARKER_SMARTPLAYLIST_QUERIES in line:
                    for name, query in _yield_name_and_queries(TAGS_MODEL):
                        fout.write(_FORMAT_NAME % name)
                        fout.write(_FORMAT_QUERY % query)
                else:
                    fout.write(line)

    print("Done !")
