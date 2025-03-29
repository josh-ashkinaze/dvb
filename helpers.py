def open_file(fn):
    with open(fn, "r") as f:
        lines = f.readlines()
    return lines

