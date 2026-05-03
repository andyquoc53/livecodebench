#!/usr/bin/env bash
set -euo pipefail

# Run from inside the LiveCodeBench repository root after the runs.
if [[ ! -d "output" ]]; then
  echo "ERROR: no output/ directory found. Run the experiments first." >&2
  exit 1
fi

python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/07_summarize_lcb_outputs.py" --output_dir output --out_dir run_summaries

zip -r lcb_run_outputs.zip output run_summaries lcb_runner/lm_styles.py lcb_runner/runner/scenario_router.py lcb_runner/runner/main.py >/dev/null

echo "Created: $(pwd)/lcb_run_outputs.zip"
echo "Upload this ZIP back to ChatGPT so the report can be updated with real results."
