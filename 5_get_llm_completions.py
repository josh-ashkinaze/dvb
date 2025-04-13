import json
import os
import time
from dotenv import load_dotenv
from tqdm import tqdm
from joblib import Parallel, delayed
import multiprocessing
from litellm import completion as litellm_completion

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

MAX_RETRIES = 3


def is_valid_completion(s):
    """
    Check if the completion has the required format.
    """
    if not isinstance(s, str):
        return False

    if "Option A" not in s:
        return False
    if "Option B" not in s:
        return False
    if "CONTEXT" not in s:
        return False

    # Check for error message
    if s.startswith("ERROR:"):
        return False

    return True


def generate_completion_with_retry(prompt, model="gpt-4o", max_retries=MAX_RETRIES):
    """
    Generate a completion with retry logic for invalid results.
    """
    retries = 0
    backoff_time = 1  # Starting backoff time in seconds

    while retries <= max_retries:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = litellm_completion(model=model, messages=messages)
            completion = response.choices[0].message.content.strip()

            if is_valid_completion(completion):
                return completion
            else:
                retries += 1
                if retries > max_retries:
                    return f"ERROR: Failed to generate valid completion after {max_retries} attempts"

                print(f"Invalid completion format. Retrying ({retries}/{max_retries})...")
                time.sleep(backoff_time)
                backoff_time *= 2

        except Exception as e:
            retries += 1
            if retries > max_retries:
                return f"ERROR: {str(e)}"

            print(f"Error: {e}. Retrying ({retries}/{max_retries})...")
            time.sleep(backoff_time)
            backoff_time *= 2

    return f"ERROR: Exceeded maximum retries ({max_retries})"


def process_json_object(json_obj, model="gpt-4o"):
    """
    Process a single JSON object by generating completions for both prompts.
    """
    train_prompt = json_obj["train_prompt"]
    test_prompt = json_obj["test_prompt"]

    train_completion = generate_completion_with_retry(train_prompt, model)
    test_completion = generate_completion_with_retry(test_prompt, model)

    result = json_obj.copy()
    result["train_completion"] = train_completion
    result["test_completion"] = test_completion

    return result



sample_preferences = "data/clean/factorial_prompt_templates_sample.json"
output_file = "data/clean/factorial_prompt_templates_with_completions.jsonl"

# Read JSONL file
jsons = []
with open(sample_preferences, "r") as f:
    for line in f:
        if line.strip():  # Skip empty lines
            jsons.append(json.loads(line.strip()))


n_cores = max(1, multiprocessing.cpu_count())
print(f"Processing {len(jsons)} examples using {n_cores} CPU cores")

results = Parallel(n_jobs=n_cores)(
    delayed(process_json_object)(json_obj)
    for json_obj in tqdm(jsons, desc="Generating completions")
)

with open(output_file, "w") as f:
    for result in results:
        f.write(json.dumps(result) + "\n")

print(f"Processed {len(results)} examples and saved results to {output_file}")