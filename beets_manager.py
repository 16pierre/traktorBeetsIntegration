from beets.library import Library


def get_rating_by_file_dict(db_file):
    result = dict()
    library = Library(db_file)
    for i in library.items():
        try:
            rating = int(float(i.rating))
            if rating >= 0 and rating <= 5:
                result[str(i.path, 'utf-8')] = int(float(i.rating))
        except Exception as e:
            continue
    return result

def write_ratings(db_file, path_to_rating_dict):
    library = Library(db_file)
    for i in library.items():
        path = str(i.path, 'utf-8')
        if path in path_to_rating_dict:
            i.rating = path_to_rating_dict.get(path)
            i.store()

