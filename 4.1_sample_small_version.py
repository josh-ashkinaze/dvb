"""
Description: Simple prompt sampler. We don't want to run the full dataset through the LLM, so we sample a subset of the data.

Input files:
- data/clean/factorial_prompt_templates.json: Full factorial prompt templates dataset

Output files:
- data/clean/factorial_prompt_templates_sample.json: Sampled dataset with 10 correlations per context and 40 trials of each one


NOTE: Explaining the numbers here as a refresher...

- We have 8 contexts
- For each, we sample 10 correlations where a correlation is a {(v1, s1)} and {(v2, s2)} grouping
    - For each correlation, we have 40 trials

- Therefore, for each context we should have 400 trials----10 correlations x 40 trials
- And in total we should have 3200 trials (400 trials per 8 context)
- [the assert statements are verifying this]
"""


import json
import pandas as pd
import random
from json import JSONDecodeError


if __name__ == "__main__":

    random.seed(42)

    N_CONFLICTS = 10

    # This is a very big file and if we just ran the generation script,
    # it may not have fully written to disk yet---leading to ValueError.
    pref_templates =  "data/clean/factorial_prompt_templates.json"

    try:
        with open(pref_templates, "r") as f:
            data = json.load(f)
    except JSONDecodeError:
        print("File may not have been fully written yet. Waiting 60 seconds...")
        import time
        time.sleep(60)
        with open(pref_templates, "r") as f:
            data = json.load(f)


    df = pd.DataFrame(data)
    df['metadata_short'] = df['metadata'].apply(lambda x: x['correlation'])
    df['context_short'] = df['context'].apply(lambda x: x['name'])
    df['metadata_and_context'] = df.apply(lambda x: f"{x['metadata_short']} - {x['context_short']}", axis=1)

    unique_metadata = df['metadata_short'].unique()
    print(f"Unique metadata: {len(unique_metadata)}")


    dfs = []

    for context in df['context_short'].unique(): # 8 contexts
        valid_metas = random.sample(list(unique_metadata), N_CONFLICTS) # 10 correlations
        context_df = df[df['context_short'] == context]
        print("length of context_df", len(context_df))
        context_df = context_df[context_df['metadata_short'].isin(valid_metas)]
        print("length of context_df after filtering for valid metas", len(context_df)) # should be 400 because each (context, correlation) pair has 40 examples
        assert len(context_df) == 400, "Context size is off!!! Check code"
        dfs.append(context_df)

    sample_df = pd.concat(dfs)
    print(len(sample_df)) # Should be 3200 b/c we have (8 contexts x 10 correlations x 40 examples)
    assert len(sample_df) == 3200, "Sample size is off!!! Check code"
    sample_df.to_json("data/clean/factorial_prompt_templates_sample.json", orient="records", lines=True)








