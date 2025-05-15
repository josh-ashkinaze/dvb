for dimension in predictiveness popularity distinctiveness; do
  python analyze_value_dimensions.py \
    --models \
      gemini/gemini-2.0-flash-lite \
      gemini/gemini-2.0-flash \
      replicate/meta/meta-llama-3-70b-instruct \
      replicate/meta/meta-llama-3-8b-instruct \
      gpt-4o-mini-2024-07-18 \
      gpt-4o-2024-08-06 \
      gpt-4.1-nano-2025-04-14 \
      gpt-4.1-mini-2025-04-14 \
      gpt-4.1-2025-04-14 \
    --dimension "$dimension" \
    --n_iters 10 \
    --output_dir data/results/fixed/value_commonality
  
done