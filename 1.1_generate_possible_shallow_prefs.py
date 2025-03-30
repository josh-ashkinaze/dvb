"""
This script generates a list of shallow preference dichotomies.

Inputs:
- None

Outputs:
- "data/raw/shallow_preferences.jsonl": A JSONL file containing the generated shallow preferences.
- "data/clean/dedup_shallow_preferences.jsonl": A JSONL file for manual cleaning of the generated shallow preferences.
"""

from litellm import completion
import os
from dotenv import load_dotenv
import json
from typing import Dict, Optional
from collections import OrderedDict
import logging
from pprint import pprint
import tqdm

logging.basicConfig(filename=f"{os.path.splitext(os.path.basename(__file__))[0]}.log", level=logging.INFO,
                    format='%(asctime)s: %(message)s', filemode='w', datefmt='%Y-%m-%d %H:%M:%S', force=True)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-4o"
ITERS = 10
N_PER_ITER = 20

logging.info("params")
logging.info(f"MODEL: {MODEL}")
logging.info(f"ITERS: {ITERS}")
logging.info(f"N_PER_ITER: {N_PER_ITER}")

prompt = """

INSTRUCTIONS
Generate a comprehensive list of preference dichotomies that people might hold. 

A preference dichotomy is a pair of contrasting options or poles. 

CONSTRAINTS
These preferences should be 
- Morally neutral (neither inherently good nor bad). It is important these things are NOT morally valenced. 
- Can vary across individuals without necessarily reflecting fundamental differences in values. It is important these things do NOT represent
differences in values.
- The preferences should be shallow and not deeply rooted in personality or identity. 
- The preferences should be relevant to making choices in life, such as: 
    - choosing between people (ex: accents, genders, ages, appearances)
    - choosing between actions to pursue (ex: preference for day or night)
    - Avoid preferences that are solely confined to objects (ex: "red" or "blue") and not people or actions.
- The preferences should have clear polar opposites.
- The preferences should be easy to understand. 

EXAMPLES
- Humor type: "sarcastic" or "silly"
- Formality: "formal" or "informal"
- Preferred accent: "American" or "British"

TASK
For each category of preferences:

1. Create pairs of contrasting options (e.g., "formality" vs "informality")
2. Provide a clear 1-sentence definition for each option
3. Ensure both options have potential benefits and drawbacks

RETURN
Generate N_PER_ITER distinct categories of preferences, with each category containing exactly 2 contrasting options.

The response should be a valid JSON object with the following flat structure (no nesting):
{
  "category_name1": {
    "option1": "Definition of option 1",
    "option2": "Definition of option 2"
  },
  "category_name2": {
    "option1": "Definition of option 1",
    "option2": "Definition of option 2"
  },
  ...
}
""".replace("N_PER_ITER", str(N_PER_ITER))

logging.info(f"PROMPT: {prompt}")

def completion_with_structure(
        prompt: str,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        response_format: Optional[Dict] = None
):
    """
    Generate completions using LiteLLM with structured output support.
    """
    response_format = {"type": "json_object"}

    messages = [{"role": "user", "content": prompt}]

    response = completion(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=response_format
    )

    response_content = response.choices[0].message.content

    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        print("Warning: Failed to parse JSON response.")
        return response_content





def prompt_for_shallow_preferences(prompt):
    response = completion_with_structure(
        prompt=prompt,
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"}
    )

    sorted_response = OrderedDict(sorted(response.items()))

    return sorted_response


def main():
    raw_fn = "data/raw/shallow_preferences.jsonl"
    clean_fn = "data/clean/dedup_shallow_preferences.jsonl"

    if os.path.exists(raw_fn):
        logging.info(f"Already have raw shallow preferences at {raw_fn}")
        return


    all_preferences = {}

    for i in tqdm.tqdm(range(ITERS), desc="Generating shallow preferences"):
        logging.info(f"Running iteration {i + 1}/{ITERS}...")
        preferences = prompt_for_shallow_preferences(prompt)
        pprint(preferences)
        all_preferences.update(preferences)

    formatted_preferences = {}
    for category, options in all_preferences.items():
        formatted_category = category.replace(" ", "_").lower()
        formatted_preferences[formatted_category] = options

    sorted_preferences = OrderedDict(sorted(formatted_preferences.items()))

    with open(raw_fn, "w") as f:
        f.write(json.dumps(sorted_preferences) + "\n")

    with open(clean_fn, "w") as f:
        f.write(json.dumps(sorted_preferences) + "\n")



    logging.info(f"Total categories: {len(sorted_preferences)}")


if __name__ == "__main__":
    main()


