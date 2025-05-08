from pprint import pprint
import pandas as pd
import json
import os
import random
from helpers import get_user_string
from collections import defaultdict
import argparse
# Set seed for reproducibility
random.seed(42)
import re


parser = argparse.ArgumentParser(description="Process LLM completions for validation.")
parser.add_argument("--full", action="store_true", help="Use the full dataset instead of the sample dataset.")
args = parser.parse_args()

suffix = "full" if args.full else "sample"

completions_fn = f"data/clean/factorial_prompt_templates_with_completions_{suffix}.jsonl"


def extract_scenarios(text_content):
    """
    Extract scenarios from the provided text content.

    Args:
        text_content (str): The raw text content with scenarios separated by '--'

    Returns:
        list: A list of dictionaries with 'context', 'choice_a', 'choice_b', and 'chosen' fields
    """
    # Split the content by the delimiter to get individual scenarios
    text_content = text_content.replace("**Option A**", "Option A")
    text_content = text_content.replace("**Option B**", "Option B")
    text_content = text_content.replace("**CONTEXT**", "CONTEXT")
    scenarios = text_content.split('--')

    # Create a list to store the parsed data
    parsed_data = []

    # Process each scenario
    for scenario in scenarios:
        # Skip empty scenarios
        if not scenario.strip():
            continue

        # Initialize a dictionary for this scenario
        scenario_data = {
            'context': '',
            'choice_a': '',
            'choice_b': '',
        }

        # Extract the context
        context_match = scenario.find("CONTEXT:")
        if context_match != -1:
            context_end = scenario.find("Option A:", context_match)
            if context_end == -1:
                context_end = len(scenario)

            context_text = scenario[context_match + len("CONTEXT:"):context_end].strip()
            scenario_data['context'] = context_text

        option_a_match = scenario.find("Option A:")
        if option_a_match != -1:
            option_a_end = scenario.find("Option B:", option_a_match)
            if option_a_end == -1:
                option_a_end = len(scenario)

            option_a_text = scenario[option_a_match + len("Option A:"):option_a_end].strip()
            scenario_data['choice_a'] = option_a_text

        option_b_match = scenario.find("Option B:")
        if option_b_match != -1:
            # Get text after "Option B:" until the end
            option_b_text = scenario[option_b_match + len("Option B:"):].strip()
            scenario_data['choice_b'] = option_b_text

        if scenario_data['context']:
            parsed_data.append(scenario_data)

    return parsed_data


# Example usage:
# with open('paste.txt', 'r') as file:
#     text_content = file.read()
# scenarios = extract_scenarios(text_content)
# print(f"Extracted {len(scenarios)} scenarios")

def wrap_text(text, width=80):
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


# Load JSONL
jsons = []
with open(completions_fn, "r") as f:
    for line in f:
        try:
            jsons.append(json.loads(line))
        except:
            pass

# Random sample (flat 100)
random_jsons = random.sample(jsons, 50)

# Output configs
csvs = {
    f"annot_output_random_{suffix}.csv": random_jsons,
}

# Main writer
for csv_fn, content in csvs.items():

    data = []
    if isinstance(content, list):
        # Random output
        for i, json_data in enumerate(content):

            try:

                metadata = json_data["metadata"]["correlation"]
                context = json_data['context']['name'] + ": " + json_data['context']['activity']
                shallow_preferences = json_data['shallow_preferences']
                deep_values = json_data['deep_values']
                example = json_data['train_completion']
                pref_option_order_train = json_data['metadata']['pref_option_order_train']

                c = extract_scenarios(example)
                choice_a_str = c[0]['choice_a']
                choice_b_str = c[0]['choice_b']
                context_str = c[0]['context']
                context_name = json_data['context']['name']
                context_activity = json_data['context']['activity']
                if pref_option_order_train == 1:
                    choice_opt_str = "A"
                # choice_a_str = f"<b>{choice_a_str}<b>"
                elif pref_option_order_train == 2:
                    choice_opt_str = "B"
                # choice_b_str = f"<b>{choice_b_str}<b>"
                data_pt = {
                    "metadata": metadata,
                    "deep_values": deep_values,
                    "shallow_preferences": shallow_preferences,
                    "context_name": context_name,
                    "context_activity": context_activity,
                    "shallow_pref_name_str": json_data['shallow_preferences']['preferred'],
                    "shallow_pref_def_str": json_data['shallow_preferences']['preferred_definition'],
                    "shallow_other_name_str": json_data['shallow_preferences']['less_preferred'],
                    "shallow_other_def_str": json_data['shallow_preferences']['less_preferred_definition'],
                    "deep_value_pref_name_str": json_data['deep_values']['preferred'].replace("_", " "),
                    "deep_value_pref_def_str": json_data['deep_values']['preferred_definition'].replace("_", " "),
                    "deep_value_other_name_str": json_data['deep_values']['less_preferred'].replace("_", " "),
                    "deep_value_other_def_str": json_data['deep_values']['less_preferred_definition'].replace("_", " "),
                    "choice_a_str": choice_a_str,
                    "choice_b_str": choice_b_str,
                    "choice_opt_str": choice_opt_str,
                    "preferred_choice": choice_a_str if pref_option_order_train == 1 else choice_b_str,
                }
                data.append(data_pt)
            except Exception as e:
                print("extracted completion on error", c)
                print(f"Error processing JSON data: {example}")
                print(f"Error processing JSON data: {e}")
                continue
        df = pd.DataFrame(data)
        df['idx'] = [i + 1 for i in range(len(df))]
        df.to_csv(f"data/clean/qualtrics_loop_merge_completion_{csv_fn}", index=False)
