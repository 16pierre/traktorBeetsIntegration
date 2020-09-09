import sys
import json
from constants import DEFAULT_PATH_FOR_JSON_FILE
import traktor
import playlist_reader
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
    folder_name = config.get("folderName")
    traktor_collection = config.get("traktor")
    playlists_dir = config.get("playlistsDir")
    beets_db = config.get("beetsLibrary")

    print(json.dumps(config, indent=4))

    print("Writing beet config...")
    beets_config_generator.write_config(config_path)

    playlists = playlist_reader.list_playlists_at_path(playlists_dir)
    print("Found %s playlists in %s: %s" % (len(playlists), playlists_dir, [p.name for p in playlists]))

    print("Writing playlists to Traktor %s playlist folder" % folder_name)
    traktor.write_custom_playlists_to_traktor_collection(
        traktor_collection,
        playlists,
        volume,
        folder_name
    )

    traktor_ratings_by_path = traktor.get_paths_to_rating_dict(traktor_collection, volume)
    print("Found %s ratings in traktor" % len(traktor_ratings_by_path))

    beets_ratings_by_path = beets_manager.get_rating_by_file_dict(beets_db)
    print("Found %s ratings in beets" % len(beets_ratings_by_path))

    if "beet_export_only" not in sys.argv:
        print("=== Exporting to beets ===")
        beets_manager.write_ratings(beets_db, traktor_ratings_by_path)

    if "traktor_export_only" not in sys.argv:
        print("=== Exporting to Traktor ===")
        beets_tags = beets_manager.get_tags_by_file_dict(beets_db, scanner.TAGS_MODEL.keys())

        not_in_traktor = list()
        for p in beets_ratings_by_path:
            if p not in traktor_ratings_by_path:
                not_in_traktor.append(p)
        not_in_beets = list()
        for p in traktor_ratings_by_path:
            if p not in beets_ratings_by_path:
                not_in_beets.append(p)
        print("Not in traktor: %s" % not_in_traktor)
        print("---------------------------")
        print("Not in beets: %s" % not_in_beets)

        print("Found %s ratings in beets db" % len(beets_ratings_by_path))
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

    # TODO: GENERER COMMENT
    print("Done !")

    elapsed_time = time.time() - start_time
    print('Execution time : %.3f' % elapsed_time)


