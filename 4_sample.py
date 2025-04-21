import json
import pandas as pd
import random

random.seed(42)

N_CONFLICTS = 10



pref_templates =  "data/clean/factorial_prompt_templates.json"
# open file

with open(pref_templates, "r") as f:
    data = json.load(f)


df = pd.DataFrame(data)
df['metadata_short'] = df['metadata'].apply(lambda x: x['correlation'])
df['context_short'] = df['context'].apply(lambda x: x['name'])
df['metadata_and_context'] = df.apply(lambda x: f"{x['metadata_short']} - {x['context_short']}", axis=1)

unique_metadata = df['metadata_short'].unique()


# Foreach context, sample 30 (v1, s1) > (v2, s2) pairtings
dfs = []

for context in df['context_short'].unique():
    # sample 30 conflicts
    valid_metas = random.sample(list(unique_metadata), N_CONFLICTS)
    context_df = df[df['context_short'] == context]
    context_df = context_df[context_df['metadata_short'].isin(valid_metas)]
    dfs.append(context_df)

sample_df = pd.concat(dfs)
print(len(sample_df))
sample_df.to_json("data/clean/factorial_prompt_templates_sample.json", orient="records", lines=True)



#
# # df['to_sample'] = df['metadata_short'].apply(lambda x: 1 if x in sample_metadata else 0)
#
# sample_df = df[df['to_sample'] == 1]
#
# sample_df.to_json("data/clean/factorial_prompt_templates_sample.json", orient="records", lines=True)
# print(f"Sampled {len(sample_df)} trials from {len(unique_metadata)} unique metadata values.")







