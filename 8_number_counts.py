loc = "data/clean/factorial_prompt_templates_with_completions_sample.jsonl"

import json

import pandas as pd
import random

random.seed(42)


# Load the completions data
jsons = []
with open(loc, "r") as f:
    for line in f:
        jsons.append(json.loads(line))

df = pd.DataFrame(jsons)
print(len(df))