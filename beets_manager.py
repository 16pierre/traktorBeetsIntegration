from beets.library import Library
import unicodedata


def get_rating_by_file_dict(db_file):
    result = dict()
    library = Library(db_file)
    for i in library.items():
        try:
            path = convert_attr_to_string(i.path)
            rating = int(float(i.rating))
            if rating >= 0 and rating <= 5:
                result[path] = int(float(i.rating))
        except Exception as e:
            continue
    return result

def get_tags_by_file_dict(db_file, tags_list):
    result = dict()
    tags_list = [tag for tag in tags_list if tag != "rating" and not tag.startswith("_")]

    library = Library(db_file)
    for i in library.items():
        try:
            path = convert_attr_to_string(i.path)
            result[path] = {tag: _get_attr_dont_throw(i, tag) for tag in tags_list}
        except Exception as e:
            print(str(i.path))
            print(e)
            # raise e
            continue
    return result

def write_ratings(db_file, path_to_rating_dict):
    library = Library(db_file)
    for i in library.items():
        path = str(i.path, 'utf-8')
        if path in path_to_rating_dict:
            i.rating = path_to_rating_dict.get(path)
            i.store()

def _get_attr_dont_throw(obj, attribute):
    if hasattr(obj, attribute):
        return str(getattr(obj, attribute))
    return None

def convert_attr_to_string(attribute):
    if attribute is None:
        return None
    result = str(attribute, 'utf-8')
    # result = result.encode('ascii')
    # result = result.decode("utf-8")
    result = unicodedata.normalize('NFKC', result)
    return result
