import numpy as np

from helpers import make_aesthetic, array_stats, categorical_stats

import pandas as pd
from scipy.stats import binomtest
import seaborn as sns
import matplotlib.pyplot as plt
from stargazer.stargazer import Stargazer

mypal = make_aesthetic()


def clean_choice(x):
    # because scale is -2, -1, 0, 1, 2 and qualtrics is 1, 2, 3, 4, 5
    # So this function turns metric into -2 to 2 in direction of <deep --> shallow>
    x = str(x)
    if "Option A" in x:
        return "A"
    elif "Option B" in x:
        return "B"
    elif "Unsure" in x:
        return "U"
    else:
        return np.nan


if __name__ == "__main__":



    df = pd.read_csv('data/raw/dvb_cb_test.csv')
    print(df.columns)

    df = df.iloc[2:]
    df = df[df['Finished']=='True']

    data = []
    for idx, row in df.iterrows():

        # participant data
        duration = row['Duration (in seconds)']
        pid = row['pid']
        educ = row['educ']
        income = row['income']
        gender = row['gender']
        age = row['Age']
        ai_usage = row['ai_usage']

        participant_data = {
            "duration": duration,
            "pid": pid,
            "educ": educ,
            "income": income,
            "gender": gender,
            "age": age,
            "ai_usage": ai_usage,
        }

        llm_shallow_cols = [x for x in df.columns if "annot_lm_two" in x]
        for col in llm_shallow_cols:
            data_pt = {
                "raw_col": col,
                "loop_merge": int(col.split("_")[0]),
                "answer_raw": row[col],
                "answer": clean_choice(row[col]),
            }
            data_pt.update(participant_data)
            data.append(data_pt)


    df = pd.DataFrame(data)
    df = df.dropna(subset=['answer'])

    meta_df = pd.read_csv('data/clean/qualtrics_loop_merge_completion_annot_output_random_sample.csv')
    df = pd.merge(df, meta_df, how='left', left_on=['loop_merge'], right_on=['idx'])

    df['correct_unsure_wrong'] = (df['answer'].str.strip() == df['choice_opt_str'].str.strip()).astype(int)

    df['correct_unsure_seperate'] = df['correct_unsure_wrong'].copy()
    df['correct_unsure_seperate'] = df['correct_unsure_seperate'].where(df['answer'] != "U", "Unsure")

    print(array_stats(df['correct_unsure_wrong'].values, include_ci=
        True))
    print()
    print(categorical_stats(df['correct_unsure_seperate'].values))

    print()
    k = len(df.query("correct_unsure_wrong==1"))
    n = len(df)
    p = 0.5

    print(f"Binomial test: {binomtest(k, n, p)}")

    print("total participants")
    print(df['pid'].nunique())






