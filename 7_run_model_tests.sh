echo "running oai models"
python3 run_model_tests.py --models gpt-4.1-nano-2025-04-14 gpt-4.1-mini-2025-04-14 gpt-4.1-2025-04-14 gpt-4o-mini-2024-07-18 gpt-4o-2024-08-06 --full

echo "running Gemini models..."
python3 run_model_tests.py --models gemini/gemini-2.0-flash-lite gemini/gemini-2.0-flash --full

echo "running llama models..."
python3 run_model_tests.py --models replicate/meta/meta-llama-3-8b-instruct replicate/meta/meta-llama-3-70b-instruct --full

echo "all model groups done"