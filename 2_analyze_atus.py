import pandas as pd
import numpy as np
import os

from helpers import replace_from_dict

# Create directories if they don't exist
os.makedirs("data/clean", exist_ok=True)

# Lists for filtering and cleaning
invalid_where = [
    "other mode of transportation",
    "don't know",
    "refused",
    "niu (not in universe)",
    "other place",
    "unspecified place"
]

invalid_activities = [
    "work (other job(s)"
]

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

# Create a preposition mapping for different locations
location_prepositions = {
    # "at" locations (enclosed spaces/establishments)
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

    # "in" locations (enclosed vehicles/spaces)
    "a person's home or yard": "in",
    "someone else's home": "in",
    "airplane": "on an",
    "driver of car, truck, or motorcycle": "while driving a",
    "passenger of car, truck, or motorcycle": "as a passenger in a",
    "subway/train": "on a",
    "bus": "on a",
    "boat/ferry": "on a",
    "taxi/limousine service": "in a",

    # "on/by" locations (outdoor/movement)
    "outdoors--not at home": "in an",
    "walking": "while",
    "bicycle": "on a"
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
        "wtg": "waiting"
    }

    act_label = replace_from_dict(act_label, rename_activities)

    act_label = act_label.replace("r's", "one's own")
    for s in act_delete_strs:
        act_label = act_label.replace(s, "")

    while "  " in act_label:
        act_label = act_label.replace("  ", " ")

    return act_label.strip()


def clean_location(loc_label):
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
    preposition = location_prepositions.get(location, "at")

    if location in ["walking", "bicycle"]:
        return f"{activity} {preposition} {location}"
    else:
        return f"{activity} {preposition} {location}"


# Main execution
# Load the ATUS data
df = pd.read_csv("data/raw/atus.csv")
print("Original columns:", df.columns)

# Apply data cleaning
################################
################################
# drop invalid locations
df = df[~df['where'].isin(invalid_where)]
# some activities are nec (not elsewhere classified) and should be dropped
df['nec'] = df['activity'].apply(lambda x: 1 if "n.e.c" in str(x) else 0)
df = df[df['nec'] == 0]
print("After dropping nec activities:", df.shape)

# clean stuff
df['activity'] = df['activity'].apply(clean_activity)
df['where'] = df['where'].apply(clean_location)
df = df[~df['activity'].isin(invalid_activities)]
df['string'] = df.apply(create_context_string, axis=1)

# Calculate frequency and duration
################################
################################
# Group by activity and location to get frequency
activity_location_freq = df.groupby(['activity', 'where']).agg(
    num_respondents=('caseid', 'nunique')
).reset_index()

total_respondents = df['caseid'].nunique()
activity_location_freq['frequency'] = activity_location_freq['num_respondents'] / total_respondents

# Calculate weighted average duration using wt06 (survey weight)
activity_location_duration = df.groupby(['activity', 'where']).apply(
    lambda x: (x['duration'] * x['wt06']).sum() / x['wt06'].sum()
).reset_index(name='avg_duration')

# Compute statistics
################################
################################
# Merge frequency and duration data
context_metrics = pd.merge(
    activity_location_freq,
    activity_location_duration,
    on=['activity', 'where']
)

# Calculate percentile ranks
context_metrics['duration_percentile'] = context_metrics['avg_duration'].rank(pct=True)
context_metrics['frequency_percentile'] = context_metrics['frequency'].rank(pct=True)
context_metrics['context_score'] = context_metrics['frequency_percentile']  # using perecentile for paper

# Sort by combined score in descending order
top_contexts = context_metrics.sort_values('context_score', ascending=False)
top_contexts_subset = top_contexts.head(50)

top_contexts_subset['string'] = top_contexts_subset.apply(create_context_string, axis=1)

top_contexts.to_json("data/clean/atus_context_metrics.jsonl", orient="records", lines=True)
