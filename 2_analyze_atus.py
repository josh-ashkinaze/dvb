"""
Author: Joshua Ashkinaze

Description: Gets the top N activities from ATUS. Specifically, we create tupples of <activity, location> and percentage of ppl
who reported doing that activity in that location (using weighted frequency). Then we save TOP_N.

Inputs:
- data/raw/atus.csv: raw atus file

Outputs:
- data/raw/atus_top_acts.jsonl: jsonl file of the top N activities
- data/clean/fixed_atus_top_acts.jsonl: jsonl file of the top N activities with manual cleaned strings
"""

import pandas as pd
import os

from helpers import replace_from_dict

TOP_N = 50

os.makedirs("data/clean", exist_ok=True)


# Remove rows with these locations because vague
invalid_where = [
    "other mode of transportation",
    "don't know",
    "refused",
    "niu (not in universe)",
    "other place",
    "unspecified place"
]

# Remove rows with these activities because vague
invalid_activities = [
    "work (other job(s)",
    "insufficient detail in verbatim"
]

# Certain strings are messy in activity labels
act_delete_strs = [
    "(2003)",
    "(2003+)",
    "(2003, 2004)",
    "(2003 only)",
    "(2004+)",
    "(2005+)",
    "(2007+)",
    "(2008+)",
    "(ex. sports)",
    "(ex. going, went, in, at)",
    "(ex groceries, food, and gas)",
    "(except hotline counseling)",
    "(except grooming)",
    "(excluding games)",
    "(not religious)",
    "(religious)",
    "(not radio)",
    "(to or from)",
    "(not veterinary care)",
    "(by self)",
    "(as a primary activity)",
    "(not related to education)",
    "(extended version)",
    "(not commuting)",
    ", inclusive",
    "n.e.c.",
]

# Create a preposition mapping for different locations.
location_prepositions = {
    # "at" locations
    "a person's workplace": "at",
    "school": "at",
    "place of worship": "at a",
    "restaurant or bar": "at a",
    "gym/health club": "at a",
    "other store/mall": "at a",
    "grocery store": "at a",
    "post office": "at the",
    "library": "at the",
    "bank": "at a",
    # "in" locations
    "a person's home or yard": "in",
    "someone else's home": "in",
    "airplane": "on an",
    "driver of car, truck, or motorcycle": "while driving a",
    "passenger of car, truck, or motorcycle": "as a passenger in a",
    "subway/train": "on a",
    "bus": "on a",
    "boat/ferry": "on a",
    "taxi/limousine service": "in a",
    # "on/by" locations
    "outdoors--not at home": "in the",
    "walking": "while",
    "bicycle": "on a",

    # as a
    "a driver of car, truck, or motorcycle": "as"
}


# Cleaning function
def clean_activity(act_label):
    if not isinstance(act_label, str):
        return act_label
    rename_activities = {
        "work, main job": "working on main job",
        "work, other job(s)": "working on side job(s)",
        "relaxing, thinking": "relaxing or thinking",
        "hh": "household",
        "trvl": "travel",
        "wtg": "waiting",
        "rsrch": "research"
    }
    act_label = replace_from_dict(act_label, rename_activities)
    act_label = act_label.replace("r's", "one's own")
    for s in act_delete_strs:
        act_label = act_label.replace(s, "")
    while "  " in act_label:
        act_label = act_label.replace("  ", " ")
    return act_label.strip()


def clean_location(loc_label):
    if not isinstance(loc_label, str): # Added check for non-string input
        return loc_label
    loc_label = loc_label.replace("r's", "one's own")
    for s in act_delete_strs:
        loc_label = loc_label.replace(s, "")
    while "  " in loc_label:
        loc_label = loc_label.replace("  ", " ")
    loc_label = loc_label.replace("home or yard", "home")
    return loc_label.strip()


# Function to create natural-sounding context strings
def create_context_string(row):
    activity = row['activity']
    location = row['where']

    cleaned_loc = clean_location(location) if isinstance(location, str) else location
    preposition = location_prepositions.get(cleaned_loc, "at") # Use cleaned loc for lookup

    if cleaned_loc in ["walking", "bicycle"]:
        return f"{activity} {preposition} {cleaned_loc}"
    else:
        return f"{activity} {preposition} {location}"



# Load data
################################
################################


df = pd.read_csv("data/raw/atus.csv")


# Apply data cleaning
################################
################################
df = df[~df['where'].isin(invalid_where)]
df['nec'] = df['activity'].apply(lambda x: 1 if "n.e.c" in str(x) else 0)
df = df[df['nec'] == 0]
print("After dropping nec activities:", df.shape)

df['activity'] = df['activity'].apply(clean_activity)
df['where'] = df['where'].apply(clean_location)
df = df[~df['activity'].isin(invalid_activities)]

# Filter out rows where cleaning might result in empty strings or NaN, if necessary
df = df.dropna(subset=['activity', 'where'])
df = df[df['activity'] != '']
df = df[df['where'] != '']

df['duration_binary'] = df['duration'].apply(lambda x: 1 if x > 1 else 0)



# Calculate frequency (weighted) and duration
################################
################################


total_weights = df['wt06'].sum()
grouped = df.groupby(['where', 'activity'])['wt06'].sum()
weight_prop = grouped / total_weights
prop_df = weight_prop.reset_index()
prop_df.columns = ['where', 'activity', 'weighted_prop']

top = prop_df.sort_values(by='weighted_prop', ascending=False).head(TOP_N)

top['string'] = top.apply(create_context_string, axis=1)

top[['string', 'activity', 'where', 'weighted_prop']].to_json("data/raw/atus_top_acts.jsonl", orient="records", lines=True)

top[['string', 'activity', 'where', 'weighted_prop']].to_json("data/clean/fixed_atus_top_acts.jsonl", orient="records", lines=True)

