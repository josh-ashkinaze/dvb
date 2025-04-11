from pprint import pprint
import pandas as pd
import json
import os
import random
from helpers import get_user_string
from collections import defaultdict

# Set seed for reproducibility
random.seed(42)

# File path
completions_fn = "data/clean/factorial_prompt_templates_with_completions.jsonl"


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

# GROUP BY CORRELATION
correlation_groups = defaultdict(list)
for item in jsons:
    correlation = item["metadata"]["correlation"]
    correlation_groups[correlation].append(item)

# Sample 10 per correlation group
grouped_samples = {
    correlation: random.sample(items, min(len(items), 10))
    for correlation, items in correlation_groups.items()
}

# Random sample (flat 100)
random_jsons = random.sample(jsons, 100)

# Output configs
json_fns = {
    "debug_output_random.md": random_jsons,
    "debug_output_correlations.md": grouped_samples
}


# Main writer
for json_fn, content in json_fns.items():
    with open(json_fn, "w") as md_file:
        md_file.write("# Factorial Prompt Templates Examples\n\n")
        md_file.write("This document contains example data from the factorial prompt templates dataset.\n\n")

        if isinstance(content, list):
            # Random output
            for i, json_data in enumerate(content):
                md_file.write(f"## Example {i + 1} of {len(content)}\n\n")

                metadata = json_data["metadata"]["correlation"]
                context = json_data['context']['name'] + ": " + json_data['context']['activity']
                shallow_preferences = json_data['shallow_preferences']
                deep_values = json_data['deep_values']
                example = json_data['train_completion']
                pref_option_order_train = json_data['metadata']['pref_option_order_train']

                # Add CHOICE based on pref_option_order
                if pref_option_order_train == 1:
                    example += "\nCHOICE: A"
                elif pref_option_order_train == 2:
                    example += "\nCHOICE: B"

                # Format and write
                formatted_context = wrap_text(context)
                formatted_context = formatted_context.replace("Option A:", "\nOption A:")\
                                                     .replace("Option B:", "\nOption B:")\
                                                     .replace("CHOICE:", "\nCHOICE:")

                md_file.write(f"### Correlation\n`{metadata}`\n\n")
                md_file.write(f"### Context\n```\n{formatted_context}\n```\n\n")

                md_file.write(f"### Shallow Preferences\n")
                md_file.write(f"- **Preferred:** {shallow_preferences['preferred']}\n")
                md_file.write(f"- **Preferred definition:** {shallow_preferences['preferred_definition']}\n")
                md_file.write(f"- **Less Preferred:** {shallow_preferences['less_preferred']}\n")
                md_file.write(f"- **Less Preferred definition:** {shallow_preferences['less_preferred_definition']}\n\n")

                md_file.write(f"### Deep Values\n")
                md_file.write(f"- **Preferred:** {deep_values['preferred']}\n")
                md_file.write(f"- **Preferred definition:** {deep_values['preferred_definition']}\n")
                md_file.write(f"- **Less Preferred:** {deep_values['less_preferred']}\n")
                md_file.write(f"- **Less Preferred definition:** {deep_values['less_preferred_definition']}\n\n")

                formatted_example = wrap_text(example)
                formatted_example = formatted_example.replace("Option A:", "\nOption A:")\
                                                     .replace("Option B:", "\nOption B:")\
                                                     .replace("CHOICE:", "\nCHOICE:")
                user_str = get_user_string("user", i)
                formatted_example = formatted_example.replace("CONTEXT: A person", f"CONTEXT: {user_str}")

                md_file.write(f"### Example Completion\n```\n{formatted_example}\n```\n\n")
                md_file.write("---\n\n")

        else:
            # Grouped by correlation
            example_counter = 1
            total_examples = sum(len(v) for v in content.values())

            for correlation, examples in sorted(content.items()):
                md_file.write(f"# Correlation: `{correlation}`\n\n")

                for example in examples:
                    context = example['context']['name'] + ": " + example['context']['activity']
                    shallow_preferences = example['shallow_preferences']
                    deep_values = example['deep_values']
                    completion = example['train_completion']
                    pref_option_order_train = example['metadata']['pref_option_order_train']

                    # Add CHOICE
                    if pref_option_order_train == 1:
                        completion += "\nCHOICE: A"
                    elif pref_option_order_train == 2:
                        completion += "\nCHOICE: B"

                    formatted_context = wrap_text(context)
                    formatted_context = formatted_context.replace("Option A:", "\nOption A:")\
                                                         .replace("Option B:", "\nOption B:")\
                                                         .replace("CHOICE:", "\nCHOICE:")

                    md_file.write(f"## Example {example_counter} of {total_examples}\n")
                    md_file.write(f"### Correlation\n`{correlation}`\n\n")

                    md_file.write(f"### Context\n```\n{formatted_context}\n```\n\n")

                    md_file.write(f"### Shallow Preferences\n")
                    md_file.write(f"- **Preferred:** {shallow_preferences['preferred']}\n")
                    md_file.write(f"- **Preferred definition:** {shallow_preferences['preferred_definition']}\n")
                    md_file.write(f"- **Less Preferred:** {shallow_preferences['less_preferred']}\n")
                    md_file.write(f"- **Less Preferred definition:** {shallow_preferences['less_preferred_definition']}\n\n")

                    md_file.write(f"### Deep Values\n")
                    md_file.write(f"- **Preferred:** {deep_values['preferred']}\n")
                    md_file.write(f"- **Preferred definition:** {deep_values['preferred_definition']}\n")
                    md_file.write(f"- **Less Preferred:** {deep_values['less_preferred']}\n")
                    md_file.write(f"- **Less Preferred definition:** {deep_values['less_preferred_definition']}\n\n")

                    formatted_example = wrap_text(completion)
                    formatted_example = formatted_example.replace("Option A:", "\nOption A:")\
                                                         .replace("Option B:", "\nOption B:")\
                                                         .replace("CHOICE:", "\nCHOICE:")
                    user_str = get_user_string("user", example_counter)
                    formatted_example = formatted_example.replace("CONTEXT: A person", f"CONTEXT: {user_str}")

                    md_file.write(f"### Example Completion\n```\n{formatted_example}\n```\n\n")
                    md_file.write("---\n\n")
                    example_counter += 1

    print(f"✅ Successfully wrote {json_fn}")
