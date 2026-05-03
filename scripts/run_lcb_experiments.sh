#!/usr/bin/env bash
set -euo pipefail

# Run from inside the official LiveCodeBench repository root.
# This wrapper delegates to the patched open-model scripts in scripts/lcb/.
# Claude Sonnet 4.6 has a separate 100-problem API run script:
#   API_SAMPLE_SIZE=100 bash /path/to/this_repo/scripts/lcb/10_run_codegen_sonnet_sample.sh
#
# Example:
#   git clone https://github.com/LiveCodeBench/LiveCodeBench.git
#   cd LiveCodeBench
#   bash /path/to/this_repo/scripts/run_lcb_experiments.sh
#
# For a 15-problem smoke test:
#   SMOKE=1 bash /path/to/this_repo/scripts/run_lcb_experiments.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LCB_SCRIPT_DIR="$SCRIPT_DIR/lcb"

if [[ ! -f "pyproject.toml" || ! -d "lcb_runner" ]]; then
  echo "ERROR: run this script from the root of the official LiveCodeBench repository." >&2
  exit 1
fi

export RELEASE_VERSION="${RELEASE_VERSION:-release_v5}"
export START_DATE="${START_DATE:-2024-08-01}"
export END_DATE="${END_DATE:-2025-01-31}"
export N="${N:-1}"
export TEMPERATURE="${TEMPERATURE:-0.2}"
export MAX_TOKENS="${MAX_TOKENS:-4096}"
export TIMEOUT="${TIMEOUT:-10}"
export NUM_PROCESS_EVALUATE="${NUM_PROCESS_EVALUATE:-4}"
export TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-1}"
export DTYPE="${DTYPE:-bfloat16}"
export LCB_MAX_MODEL_LEN="${LCB_MAX_MODEL_LEN:-8192}"
export VLLM_GPU_MEMORY_UTILIZATION="${VLLM_GPU_MEMORY_UTILIZATION:-0.90}"
export CACHE_BATCH_SIZE="${CACHE_BATCH_SIZE:-25}"

bash "$LCB_SCRIPT_DIR/01_setup_lcb.sh"
bash "$LCB_SCRIPT_DIR/03_run_codegen_qwen.sh"
bash "$LCB_SCRIPT_DIR/04_run_codegen_deepseek.sh"
bash "$LCB_SCRIPT_DIR/05_run_selfrepair_qwen.sh"
bash "$LCB_SCRIPT_DIR/06_run_selfrepair_deepseek.sh"
bash "$LCB_SCRIPT_DIR/08_collect_results.sh"
