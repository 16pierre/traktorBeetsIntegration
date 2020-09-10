import sys
import json
from constants import DEFAULT_PATH_FOR_JSON_FILE
import traktor
import m3u_playlist_reader
import beets_manager
import beets_config_generator
import scanner
import time


if __name__ == "__main__":

    start_time = time.time()

    if len(sys.argv) < 2:
        config_path = DEFAULT_PATH_FOR_JSON_FILE
    else:
        config_path = sys.argv[1]

    with open(config_path) as json_file:
        config = json.load(json_file)

    volume = config.get("volume")

    traktor_collection = config.get("traktor")
    beets_db = config.get("beetsLibrary")

    # Smart playlist plugin
    beet_smart_playlist_path = config.get("m3uPath")
    beet_smart_playlist_directory_name = config.get("m3uDirectoryName")

    print(json.dumps(config, indent=4))

    print("Writing beet config...")
    beets_config_generator.write_config(config_path)

    beet_smart_playlists = m3u_playlist_reader.list_playlists_at_path(beet_smart_playlist_path)
    print("Found %s beet smart playlists in %s: %s" %
          (len(beet_smart_playlists), beet_smart_playlist_path, [p.name for p in beet_smart_playlists]))

    print("Writing beet smart playlists to Traktor %s playlist folder" % beet_smart_playlist_directory_name)
    traktor.write_auto_generated_playlists_to_traktor(
        traktor_collection,
        beet_smart_playlists,
        volume,
        beet_smart_playlist_directory_name
    )

    traktor_tracks = traktor.get_tracks(traktor_collection, volume)
    print("Found %s ratings in traktor" % len([t for t in traktor_tracks.values() if t.rating is not None]))

    beets_tracks = beets_manager.get_tracks(beets_db, scanner.TAGS_MODEL.keys())
    print("Found %s ratings in beets" % len([t for t in beets_tracks.values() if t.rating is not None]))

    if "beet_export_only" not in sys.argv:
        print("=== Exporting ratings to beets ===")
        beets_manager.write_ratings(beets_db, traktor_tracks)

    if "traktor_export_only" not in sys.argv:
        print("=== Exporting ratings to Traktor ===")

        not_in_traktor = list()
        for p in beets_tracks:
            if beets_tracks.get(p).rating is not None and \
                    (p not in traktor_tracks or traktor_tracks.get(p).rating is None):
                not_in_traktor.append(beets_tracks.get(p))
        not_in_beets = list()
        for p in traktor_tracks:
            if traktor_tracks.get(p).rating is not None and\
                    (p not in beets_tracks or beets_tracks.get(p).rating is None):
                not_in_beets.append(traktor_tracks.get(p))
        print("Ratings not in traktor: total %s, extract: %s" %
              (len(not_in_traktor), [str(t) for t in not_in_traktor[:10]]))
        print("---------------------------")
        print("Ratings not in beets: total %s, extract: %s" %
              (len(not_in_beets), [str(t) for t in not_in_beets[:10]]))

        traktor.write_rating_to_traktor_collection(
            traktor_collection,
            beets_tracks
        )

        print("Writing comments to Traktor tracks...")
        traktor.write_comments_to_traktor_collection(
            traktor_collection,
            beets_tracks,
            scanner.TAGS_MODEL.keys()
        )

    print("Done !")

    elapsed_time = time.time() - start_time
    print('Execution time : %.3f' % elapsed_time)


