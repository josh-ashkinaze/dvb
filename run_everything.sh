#!/bin/bash

# Exit on any error
set -e

if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

echo "Creating new virtual environment..."
python3 -m venv venv

echo "Installing requirements..."
venv/bin/pip install -r requirements.txt

# Activate the virtual environment
source venv/bin/activate
echo "Virtual environment activated"

#echo "Step 1.1: Generate possible shallow prefs"
#python 1.1_generate_possible_shallow_prefs.py
#
#echo "Step 1.2: Clean shallow prefs"
#python 1.2_clean_shallow_prefs.py
#
#echo "Step 1.3: Generate annotation data"
#python 1.3_generate_shallow_annotation_data.py

echo "Step 3: Generate prompts"
python 3_generate_prompts.py

echo "Step 4: Sample data"
python 4_sample.py

echo "Step 5.1: Sample LLM completions for debug"
python 5.1_sample_llm_completions_for_debug.py

echo "Step 5: Get LLM completions"
python 5_get_llm_completions.py

echo "Step 5.1: Sample LLM completions for debug"
python 5.1_sample_llm_completions_for_debug.py

echo "Step 6: Make test sets"
python 6_make_tests.py

echo "Step 7: Run model tests"
python 7_run_model_tests.py

echo "Step 8: Number counts"
python 8_number_counts.py

echo "Step 9: Run final stats notebook"
papermill 9_run_stats.ipynb 9_run_stats_output.ipynb

echo "🏁 All steps completed successfully!"
