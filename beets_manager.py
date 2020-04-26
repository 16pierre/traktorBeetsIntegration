from beets.library import Library


def get_rating_by_file_dict(db_file):
    result = dict()
    for i in Library("/Users/16pierre/beets/musiclibrary.db").items():
        try:
            rating = int(i.rating)
            if rating >= 0 and rating < 5:
                result[str(i.path, 'utf-8')] = int(i.rating)
        except Exception:
            continue
    return result

