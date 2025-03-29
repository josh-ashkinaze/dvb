def open_file(fn):
    with open(fn, "r") as f:
        lines = f.readlines()
    return lines

def replace_from_dict(string, replacements):
    for old, new in replacements.items():
        string = string.replace(old, new)
    return string

