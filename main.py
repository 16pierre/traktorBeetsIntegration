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
    beet_smart_playlist_path = config.get("beetSmartPlaylistsPath")
    beet_smart_playlist_directory_name = config.get("beetSmartPlaylistDirectoryName")

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

    traktor_ratings_by_path = traktor.get_paths_to_rating_dict(traktor_collection, volume)
    print("Found %s ratings in traktor" % len(traktor_ratings_by_path))

    beets_ratings_by_path = beets_manager.get_rating_by_file_dict(beets_db)
    print("Found %s ratings in beets" % len(beets_ratings_by_path))

    if "beet_export_only" not in sys.argv:
        print("=== Exporting ratings to beets ===")
        beets_manager.write_ratings(beets_db, traktor_ratings_by_path)

    if "traktor_export_only" not in sys.argv:
        print("=== Exporting ratings to Traktor ===")
        beets_tags = beets_manager.get_tags_by_file_dict(beets_db, scanner.TAGS_MODEL.keys())

        not_in_traktor = list()
        for p in beets_ratings_by_path:
            if p not in traktor_ratings_by_path:
                not_in_traktor.append(p)
        not_in_beets = list()
        for p in traktor_ratings_by_path:
            if p not in beets_ratings_by_path:
                not_in_beets.append(p)
        print("Ratings not in traktor: %s" % not_in_traktor)
        print("---------------------------")
        print("Ratings not in beets: %s" % not_in_beets)

        traktor.write_rating_to_traktor_collection(
            traktor_collection,
            beets_ratings_by_path
        )

        print("Writing comments to Traktor tracks...")
        traktor.write_comments_to_traktor_collection(
            traktor_collection,
            beets_tags,
            scanner.TAGS_MODEL.keys()
        )

    print("Done !")

    elapsed_time = time.time() - start_time
    print('Execution time : %.3f' % elapsed_time)


