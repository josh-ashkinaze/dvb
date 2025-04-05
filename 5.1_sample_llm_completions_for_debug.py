from pprint import pprint
import pandas as pd
import json
import os
import random

# Read in jsons
###########################
completions_fn = "data/clean/factorial_prompt_templates_with_completions.jsonl"
output_md_file = "debug_output.md"  # Output filename

jsons = []
with open(completions_fn, "r") as f:
    for line in f:
        try:
            jsons.append(json.loads(line))
        except:
            pass

with open(output_md_file, "w") as md_file:
    md_file.write("# Factorial Prompt Templates Examples\n\n")
    md_file.write("This document contains example data from the factorial prompt templates dataset.\n\n")

    random_jsons = random.sample(jsons, 100)

    for i, json_data in enumerate(random_jsons):
        # Extract data
        metadata = json_data["metadata"]['correlation']
        context = json_data['context_short']
        shallow_preferences = json_data['shallow_preferences']
        deep_values = json_data['deep_values']
        example = json_data['train_completion']
        pref_option_order_train = json_data['metadata']['pref_option_order_train']

        if pref_option_order_train == 1:
            example += "\nCHOICE: A"
        elif pref_option_order_train == 2:
            example += "\nCHOICE: B"

        md_file.write(f"## Example {i + 1} of {len(random_jsons)}\n\n")
        md_file.write(f"### Metadata\n")
        md_file.write(f"Correlation: `{metadata}`\n\n")

        md_file.write(f"### Context\n")


        # Function to wrap text to prevent overflow
        def wrap_text(text, width=80):
            words = text.split()
            lines = []
            current_line = []
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 <= width:  # +1 for the space
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = len(word)

            if current_line:
                lines.append(" ".join(current_line))

            return "\n".join(lines)


        formatted_context = wrap_text(context)
        formatted_context = formatted_context.replace("Option A:", "\nOption A:").replace("Option B:",
                                                                                          "\nOption B:").replace(
            "CHOICE:", "\nCHOICE:")

        md_file.write(f"```\n{formatted_context}\n```\n\n")
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

        md_file.write(f"### Example Completion\n")

        formatted_example = wrap_text(example)
        formatted_example = formatted_example.replace("Option A:", "\nOption A:").replace("Option B:",
                                                                                          "\nOption B:").replace(
            "CHOICE:", "\nCHOICE:")

        md_file.write(f"```\n{formatted_example}\n```\n\n")

        md_file.write("---\n\n")

print(f"Successfully wrote {len(random_jsons)} examples to {output_md_file}")