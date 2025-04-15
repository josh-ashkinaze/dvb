"""
Author: Joshua Ashkinaze

Description: Make a CSV file for Qualtrics loop and merge.

Inputs:
- data/clean/fixed_preferences.json

Outputs:
- data/clean/qualtrics_loop_merge_deep_shallow.csv: Combined deep and shallow
- data/clean/qualtrics_loop_merge_shallow.csv: Shallow only

The structure of this is that we have a col for `idx' which is the loop and merge index. So then we will merge the qualtrics data
on this file to get the preferences back.
"""
import itertools


import pandas as pd
import json
from pprint import pprint

def clean_string(s):
    """
    Cleans the string by removing any unwanted characters.
    """
    s = s.replace("_", " ")
    s = s.title()
    return s


if __name__ == "__main__":
    with open("data/clean/fixed_preferences.json") as f:
        preferences = json.load(f)
        print(f"Loaded {len(preferences)} preference categories")

    # load deep values
    with open("data/clean/deep_values.json") as f:
        deep_values = json.load(f)['prima_facie']
        print(f"Loaded {len(deep_values)} deep values")

    deep_pairs = list(itertools.combinations(deep_values.keys(), 2))

    data = []
    for x in preferences:
        data_pt = {}
        data_pt["name"] = x.replace("_", " ").title()
        keys = list(preferences[x].keys())  # Ensure keys are converted to a list
        name_1 = clean_string(keys[0])
        name_1_def = preferences[x][keys[0]]  # Use the original key

        name_2 = clean_string(keys[1])
        name_2_def = preferences[x][keys[1]]  # Use the original key

        data_pt['name1'] = name_1
        data_pt['name1_def'] = name_1_def
        data_pt['name2'] = name_2
        data_pt['name2_def'] = name_2_def
        data_pt['set'] = 'shallow'
        data.append(data_pt)

    for x in deep_pairs:
        data_pt = {}
        data_pt["name"] = f"{clean_string(x[0])} or {clean_string(x[1])}"
        name_1 = clean_string(x[0])
        name_1_def = deep_values[x[0]]

        name_2 = clean_string(x[1])
        name_2_def = deep_values[x[1]]

        data_pt['name1'] = name_1
        data_pt['name1_def'] = name_1_def.replace("An Agent should", "Preferring AI Agents that")
        data_pt['name2'] = name_2
        data_pt['name2_def'] = name_2_def.replace("An Agent should", "Preferring AI Agents that")
        data_pt['set'] = 'deep'
        data.append(data_pt)

    df = pd.DataFrame(data)
    df['idx'] = [i+1 for i in range(len(df))]
    df.to_csv("data/clean/qualtrics_loop_merge_deep_shallow_prima.csv", index=False)
    shallow = df[df['set'] == 'shallow']
    shallow.to_csv("data/clean/qualtrics_loop_merge_shallow.csv", index=False)

    # samples
    for idx, row in df.iterrows():
        pprint(f"Row {idx}: {row.to_dict()}")




