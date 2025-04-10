import random

def open_file(fn):
    with open(fn, "r") as f:
        lines = f.readlines()
    return lines

def replace_from_dict(string, replacements):
    for old, new in replacements.items():
        string = string.replace(old, new)
    return string




def get_user_string(how, seed):
    random.seed(seed)
    random_int = str(random.randint(100, 10000))

    if how=="user":
        person_str = "user"
    elif how=="person":
        person_str = "person"

    user_id = f"{person_str}{random_int}"
    return user_id
