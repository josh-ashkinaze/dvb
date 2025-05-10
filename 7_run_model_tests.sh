#!/bin/bash
# Run DVB models with three options: final, trial, or test

how="trial" # [final, trial]

if [ "$how" = "final" ]; then
    echo "Running FINAL tests (full dataset)..."

    python3 run_model_tests.py --models \
        gpt-4.1-nano-2025-04-14 \
        gpt-4.1-mini-2025-04-14 \
        gpt-4.1-2025-04-14 \
        gpt-4o-mini-2024-07-18 \
        gpt-4o-2024-08-06 \
        gemini/gemini-2.0-flash-lite \
        gemini/gemini-2.0-flash \
        replicate/meta/meta-llama-3-8b-instruct \
        replicate/meta/meta-llama-3-70b-instruct \
        --full

elif [ "$how" = "trial" ]; then
    echo "Running small batch"
    max_tests=5

    python3 run_model_tests.py --models \
        gpt-4.1-nano-2025-04-14 \
        gpt-4.1-mini-2025-04-14 \
        gpt-4.1-2025-04-14 \
        gpt-4o-mini-2024-07-18 \
        gpt-4o-2024-08-06 \
        gemini/gemini-2.0-flash-lite \
        gemini/gemini-2.0-flash \
        replicate/meta/meta-llama-3-8b-instruct \
        replicate/meta/meta-llama-3-70b-instruct \
        --full --max_tests $max_tests

fi

echo "All models completed!"