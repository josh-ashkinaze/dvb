"""
Author: Joshua Ashkinaze

Description: Cleans the shallow preferences JSON file.

Inputs:
- data/clean/dedup_shallow_preferences.jsonl

Outputs:
- data/clean/fixed_preferences.json

"""


import json
import re


def fix_json_file(input_path, output_path):
    """
    Fix common JSON syntax errors like trailing commas and save to a new file.
    Returns the parsed JSON data if successful.
    """
    print(f"Reading from {input_path}...")

    with open(input_path, 'r') as f:
        content = f.read()

    fixed_content = re.sub(r',(\s*})', r'\1', content)

    try:
        data = json.loads(fixed_content)
        print(f"Successfully parsed JSON with {len(data)} items")

        # Save the fixed content
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Fixed JSON saved to {output_path}")

        return data
    except json.JSONDecodeError as e:
        print(f"Error: JSON still has issues: {e}")
        return None


if __name__ == "__main__":
    input_file = "data/clean/dedup_shallow_preferences.jsonl"
    output_file = "data/clean/fixed_preferences.json"

    preferences = fix_json_file(input_file, output_file)

    if preferences:
        print(f"\nLoaded {len(preferences)} preference categories")

        sample_categories = list(preferences.keys())[:3]
        print("\nSample categories:")
        for category in sample_categories:
            print(f"- {category}: {list(preferences[category].keys())}")