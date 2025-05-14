"""
Value Dimensions Analysis Script (Revised)

This script queries LLMs to rate different values on three key dimensions:
1. Popularity - How commonly held is the value in society
2. Distinctiveness - How conceptually distinct the value is from other values
3. Behavioral Predictiveness - How well the value predicts user preferences/behavior

Usage:
    python analyze_value_dimensions.py --dimension "popularity" --models gpt-4o-2024-08-06 --n_iters 10
    python analyze_value_dimensions.py --dimension "distinctiveness" --models gpt-4o-2024-08-06 --n_iters 10
    python analyze_value_dimensions.py --dimension "predictiveness" --models gpt-4o-2024-08-06 --n_iters 10

Arguments:
    --dimension: Specific dimension to analyze (required)
    --models: List of models to test (default: all available models)
    --n_iters: Number of iterations to run per value-model pair (default: 5)
    --output_dir: Directory to save results (default: "data/value_dimensions/")
"""

import argparse
import json
import logging
import multiprocessing
import os
import random
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import pandas as pd
from dotenv import load_dotenv
from litellm import completion
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Set random seed for reproducibility
random.seed(42)

# Define all available models
ALL_MODELS = [
    "gemini/gemini-2.0-flash-lite",
    "gemini/gemini-2.0-flash",
    "replicate/meta/meta-llama-3-70b-instruct",
    "replicate/meta/meta-llama-3-8b-instruct",
    "gpt-4o-mini-2024-07-18",
    "gpt-4o-2024-08-06",
    "gpt-4.1-nano-2025-04-14",
    "gpt-4.1-mini-2025-04-14",
    "gpt-4.1-2025-04-14"
]

# Define the values to be analyzed
# Prima facie duties
PRIMA_FACIE_VALUES = {
    "beneficence": "An Agent should act to benefit others",
    "fidelity": "An Agent should keep its promises and tell the truth",
    "justice": "An Agent should treat people fairly and equitably",
    "non_maleficence": "An Agent should not harm others",
    "reparation": "An Agent should correct past errors",
    "self_improvement": "An Agent should work to improve its capabilities"
}

# Schwartz's basic values
SCHWARTZ_VALUES = {
    "security": "An Agent should prioritize safety and stability in society",
    "conformity": "An Agent should comply with rules and avoid actions that might upset others",
    "tradition": "An Agent should respect customs and ideas provided by traditional cultures",
    "universalism": "An Agent should understand, appreciate, and protect the welfare of all people and nature",
    "benevolence": "An Agent should preserve and enhance the welfare of those with whom one is in frequent contact"
}

# Combine all values
ALL_VALUES = {**PRIMA_FACIE_VALUES, **SCHWARTZ_VALUES}

# Define the dimensions and their descriptions
DIMENSIONS = {
    "popularity": "How commonly held is [VALUE_NAME] in contemporary society? (Where 1 means this value is held by very few people, and 10 means this value is widely held across nearly all segments of society)",

    "distinctiveness": "How conceptually distinct is [VALUE_NAME] from other related values? (Where 1 means it substantially overlaps with and is difficult to distinguish from other values, and 10 means this value occupies a unique conceptual space with minimal overlap with other values)",

    "predictiveness": "How strongly does knowing someone prioritizes [VALUE_NAME] predict their preferences and behaviors? (Where 1 means knowing someone values this tells you very little about their likely choices, and 10 means this value strongly and consistently predicts specific preferences)"
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze value dimensions across different LLMs.")
    parser.add_argument("--dimension", type=str, required=True, choices=DIMENSIONS.keys(),
                        help="Specific dimension to analyze")
    parser.add_argument("--models", nargs="+", choices=ALL_MODELS, default=ALL_MODELS,
                        help="Specific models to test (default: all models)")
    parser.add_argument("--n_iters", type=int, default=5,
                        help="Number of iterations to run per value-model pair (default: 5)")
    parser.add_argument("--output_dir", type=str, default="data/value_dimensions/",
                        help="Directory to save results (default: 'data/value_dimensions/')")

    return parser.parse_args()


def setup_logging(args):
    """Set up logging configuration."""
    datetime_str = time.strftime("%Y%m%d-%H%M%S")

    # Create output directory if it doesn't exist
    dimension_dir = f"{args.output_dir}"
    os.makedirs(dimension_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{dimension_dir}/{args.dimension}_{datetime_str}.log"),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Starting Value Dimension Analysis: {args.dimension}")
    logging.info(f"Arguments: models={args.models}, n_iters={args.n_iters}, output_dir={args.output_dir}")

    return datetime_str, dimension_dir


def generate_dimension_prompt(dimension, dimension_description, value_name, value_definition):
    """Generate a prompt to query a specific dimension of a value."""
    return f"""On a scale from 1 to 10, {dimension_description.replace('[VALUE_NAME]', value_name)}

VALUE: {value_name}
DEFINITION: {value_definition}

Please provide only a single number between 1 and 10 as your answer, with no additional text."""


def parse_rating(response_text):
    """Extract a numerical rating from the model's response."""
    # First try to extract just a number
    import re

    # Look for standalone digits 1-10
    matches = re.findall(r'\b([1-9]|10)\b', response_text)
    if matches:
        return int(matches[0])

    # Look for numbers with decimal points
    matches = re.findall(r'\b([1-9]|10)\.?[0-9]?\b', response_text)
    if matches:
        # Round to nearest integer
        return round(float(matches[0]))

    # If no clear match, check if there are words that indicate ratings
    rating_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    for word, rating in rating_words.items():
        if word in response_text.lower():
            return rating

    # If nothing else works, look for any digits
    digits = re.findall(r'\d+', response_text)
    if digits:
        # Convert to int and ensure it's in range 1-10
        num = int(digits[0])
        if 1 <= num <= 10:
            return num
        elif num > 10:
            return 10
        else:
            return 1

    # If we really can't find anything, return None
    return None


def query_model(model_name, dimension, dimension_description, value_name, value_definition, iteration):
    """Query a model for a value dimension rating with retries."""
    prompt = generate_dimension_prompt(dimension, dimension_description, value_name, value_definition)

    max_retries = 5
    backoff_time = 2  # seconds
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = completion(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,  # We only need a short answer
                timeout=30,  # Set timeout to prevent hanging
            )

            raw_response = response.choices[0].message.content.strip()
            rating = parse_rating(raw_response)

            if rating is not None:
                return {
                    "model": model_name,
                    "dimension": dimension,
                    "value_name": value_name,
                    "value_definition": value_definition,
                    "iteration": iteration,
                    "raw_response": raw_response,
                    "rating": rating,
                    "success": True,
                    "error": None
                }
            else:
                retry_count += 1
                logging.warning(
                    f"Could not parse rating from response: '{raw_response}'. Retry {retry_count}/{max_retries}")
                time.sleep(backoff_time * (2 ** (retry_count - 1)))

        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            logging.warning(f"Error querying {model_name} for {dimension} of {value_name}, attempt {retry_count}: {error_msg}")

            if retry_count >= max_retries:
                return {
                    "model": model_name,
                    "dimension": dimension,
                    "value_name": value_name,
                    "value_definition": value_definition,
                    "iteration": iteration,
                    "raw_response": None,
                    "rating": None,
                    "success": False,
                    "error": error_msg,
                    "traceback": traceback.format_exc()
                }

            time.sleep(backoff_time * (2 ** (retry_count - 1)))


def run_analysis(args, datetime_str, dimension_dir):
    """Run the value dimension analysis across models."""
    # Determine number of worker threads
    n_workers = max(1, multiprocessing.cpu_count() - 1)
    logging.info(f"Using {n_workers} workers for parallel processing")

    dimension = args.dimension
    dimension_description = DIMENSIONS[dimension]

    all_results = []

    # Create all tasks to run
    tasks = []
    for model_name in args.models:
        for value_name, value_definition in ALL_VALUES.items():
            for iteration in range(1, args.n_iters + 1):
                tasks.append((model_name, dimension, dimension_description, value_name, value_definition, iteration))

    # Shuffle tasks to avoid bunching up requests to same model/API
    random.shuffle(tasks)

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []

        # Submit all tasks
        for task in tasks:
            future = executor.submit(query_model, *task)
            futures.append(future)

        # Process results as they complete
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Processing {dimension} queries"):
            try:
                result = future.result()
                all_results.append(result)

                # Log success or failure
                if result["success"]:
                    logging.info(f"Success: {result['model']} rated {result['dimension']} of {result['value_name']} as {result['rating']}")
                else:
                    logging.error(f"Failed: {result['model']} could not rate {result['dimension']} of {result['value_name']}: {result['error']}")

            except Exception as e:
                logging.error(f"Unexpected error processing result: {str(e)}")

    # Convert results to DataFrame
    results_df = pd.DataFrame(all_results)

    # Save raw results
    output_file = f"{dimension_dir}/{dimension}_raw_{datetime_str}.csv"
    results_df.to_csv(output_file, index=False)
    logging.info(f"Saved raw results to {output_file}")




def main():
    """Main function to run the value dimension analysis."""
    args = parse_arguments()
    datetime_str, dimension_dir = setup_logging(args)
    run_analysis(args, datetime_str, dimension_dir)


if __name__ == "__main__":
    main()