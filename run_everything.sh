#!/bin/bash

# Basic script that runs everything in order with a virtual environment
# Exit on error
set -e

echo "============================================"
echo "RUNNING EVERYTHING"
echo "============================================"

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Running data preparation scripts..."
python 1.1_generate_possible_shallow_prefs.py
python 1.2_clean_shallow_prefs.py
python 1.3_generate_annotation_data.py

echo "Running analysis scripts..."
python 2.1_generate_annotation_prompts.py
python 2_analyze_atus.py

echo "Running generation scripts..."
python 3_generate_prompts.py

echo "Running sampling scripts..."
python 4_sample.py
python 5.1_sample_llm_completions_for_debug.py
python 5_get_llm_completions.py

echo "Running testing scripts..."
python 6_make_tests.py
python 7_run_model_tests.py
python 8_number_counts.py

echo "Running statistics with papermill..."
papermill 9_run_stats.ipynb 9_run_stats_output.ipynb

# Deactivate virtual environment
deactivate

echo "Pipeline execution completed successfully!"