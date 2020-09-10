from typing import List


def identify_value_from_prefix(value: str, values: List[str]):
    for v in values:
        if v.startswith(value):
            return v


def identify_compressed_value(value, values):
    if isinstance(values[0], int):
        try:
            parsed_input = int(value)
            if parsed_input in values:
                return parsed_input
        except Exception:
            return None
    else:
        value = value.lower()
        lowercase_values = [v.lower() for v in values]
        try:
            found = lowercase_values.index(value)
            return values[found]
        except:
            ...
        compatible_values = [v for v in lowercase_values
                             if _are_strings_compatible(value, v)]
        if len(compatible_values) == 1:
            return values[lowercase_values.index(compatible_values[0])]
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
