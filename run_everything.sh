##!/bin/bash
#
## Exit on any error
#set -e
#
#if [ -d "venv" ]; then
#    echo "Removing existing virtual environment..."
#    rm -rf venv
#fi
#
#echo "Creating new virtual environment..."
#python3 -m venv venv
#
#echo "Installing requirements..."
#venv/bin/pip install -r requirements.txt
#
## Activate the virtual environment
#source venv/bin/activate
#echo "Virtual environment activated"
#
#
##!/bin/bash
#
## Run pipeline script for shallow preference model project
## This script runs the files in the correct order shown in the project structure
#
## Exit on error
#set -e
#
## Print execution steps
#set -x
#
## Setup virtual environment first
#bash 0_setup_venv.sh
#
## Activate virtual environment (assuming it creates a venv directory)
#source venv/bin/activate
#
#######################################################
#######################################################
## PART A: Getting YC domains
#######################################################
#######################################################
#
## Data scraping and preparation
#python3 0.1_scrape_yc.py
## run 0.2_map_onet.ipynb
#
#
#######################################################
#######################################################
## PART B: Shallow vs deep
#######################################################
#######################################################
#python3 1.1_generate_possible_shallow_prefs.py
#python3 1.2_clean_shallow_prefs.py
#python3 1.3_generate_shallow_annotation_data.py
## run 1.4_shallow_pref_annot_analysis.ipynb
#
#
#######################################################
#######################################################
## PART C: Full factorial prompts
#######################################################
#######################################################
#python3 3_generate_prompts.py
#
#
#######################################################
#######################################################
## PART D: Running sample pipeline
## We generated a smaller batch of data first
#######################################################
#######################################################
#
#python3 4.1_sample_small_version.py
#python3 5.0_get_llm_completions.py --sample
#python3 5.1_sample_llm_completions_for_debug.py
#python3 5.2_sample_llm_completions_for_evaluation.py
#python3 5.3_analyze_cb_test.py
#
#######################################################
#######################################################
## PART D: Running full pipeline
## Now we are going to fetch the full completions,
## not the sample since cb_test worked out
#######################################################
#######################################################
#
#python3 4.1 sample_big_version.py
#python3 5.0_get_llm_completions.py --full
#python3 5.1_sample_llm_completions_for_debug.py -- full
#python3 5.2_sample_llm_completions_for_evaluation.py --full
#
#######################################################
#######################################################
## PART E: Making and running tests
## Now we are going to fetch the full completions,
## not the sample since cb_test worked out
#######################################################
#######################################################
#python3 old_6_make_tests_old.py
#python3 7_run_model_tests.py
#
#
#
