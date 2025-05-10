"""
Description: Simple prompt sampler. We don't want to run the full dataset through the LLM, so we sample a subset of the data.

Input files:
- data/clean/factorial_prompt_templates.json: Full factorial prompt templates dataset

Output files:
- data/clean/factorial_prompt_templates_final.json: Sampled dataset with 100 correlations per context and 40 trials of each one (40 * 100 * 8 = 32000 completions)


NOTE: Explaining the numbers here as a refresher...

- We have 8 contexts
- For each, we sample 50 correlations where a correlation is a {(v1, s1)} and {(v2, s2)} grouping
    - For each correlation, we have 40 trials

- So, in total we have 8 * 50 * 40 = 16000 trials
"""


import json
import pandas as pd
import random
from json import JSONDecodeError
import logging 
import os
import numpy as np


logging.basicConfig(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}.log", level=logging.INFO, format='%(asctime)s: %(message)s', filemode='w', datefmt='%Y-%m-%d %H:%M:%S', force=True)




if __name__ == "__main__":


    random.seed(42)
    np.random.seed(42)

    # # This is a very big file and if we just ran the generation script,
    # # it may not have fully written to disk yet---leading to ValueError.
    pref_templates =  "data/clean/factorial_prompt_templates.json"

    try:
        with open(pref_templates, "r") as f:
            data = json.load(f)
    except JSONDecodeError:
        logging.info("File may not have been fully written yet. Waiting 60 seconds...")
        import time
        time.sleep(60)
        with open(pref_templates, "r") as f:
            data = json.load(f)


    df = pd.DataFrame(data)

    df['correlation'] = df['metadata'].apply(lambda x: x['correlation'])
    logging.info("unique correlations: %d", len(df['correlation'].unique()))
    df['context_short'] = df['context'].apply(lambda x: x['name'])
    logging.info("unique contexts: %d", len(df['context_short'].unique()))


    samples = []
    counter = 0
    import numpy as np
    for context in df['context_short'].unique(): #8 contexts
        sample_correlations = np.random.choice(df['correlation'].unique(), 50, replace=False)
        # 100 (v1, v2) vs (s1, s2) pairs
        # Each of (context, v1, v2, s1, s2) should appear 40 times
        # So we should have in total: 8 * 50 * 40 = 16000
        counter += 1
        temp_df = df[df['context_short'] == context]
        temp_df = temp_df[temp_df['correlation'].isin(sample_correlations)]
        samples.append(temp_df)

    sample_df = pd.concat(samples)
    logging.info(len(sample_df))


    ############## ASSERTIONS TO MAKE SURE DATA FORMAT CORRECT ##############
    sample_df['context_correlation'] = sample_df.apply(lambda x: f"{x['context_short']} - {x['correlation']}", axis=1)

    assert len(sample_df) == 16000, "Sample size is off!!! Check code"

    assert len(sample_df['context_short'].unique()) == 8, "Context size is off!!! Check code"

    context_correlation_counts = sample_df['context_correlation'].value_counts().to_list()
    assert all([x == 40 for x in context_correlation_counts]), "Context correlation counts are off!!! Check code"


    sample_df.to_json("data/clean/factorial_prompt_templates_full.json", orient="records", lines=True)
    




