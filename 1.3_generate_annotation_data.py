"""
Author: Joshua Ashkinaze

Description: Make a CSV file for Qualtrics loop and merge.

Inputs:
- data/clean/fixed_preferences.json

Outputs:
- data/clean/qualtrics_loop_merge.csv

The structure of this is that we have a col for `idx' which is the loop and merge index. So then we will merge the qualtrics data
on this file to get the preferences back.
"""


import pandas as pd
import json

if __name__ == "__main__":
    with open("data/clean/fixed_preferences.json") as f:
        preferences = json.load(f)


    data = []
    for x in preferences:
        data_pt = {}
        data_pt["name"] = x.replace("_", " ").title()
        keys = preferences[x].keys()
        name_1 = list(keys)[0]
        name_1_def = preferences[x][name_1]

        name_2 = list(keys)[1]
        name_2_def = preferences[x][name_2]

        data_pt['name1'] = name_1
        data_pt['name1_def'] = name_1_def
        data_pt['name2'] = name_2
        data_pt['name2_def'] = name_2_def
        data.append(data_pt)

    df = pd.DataFrame(data)
    df['idx'] = [i+1 for i in range(len(df))]
    df.to_csv("data/clean/qualtrics_loop_merge.csv", index=False)



