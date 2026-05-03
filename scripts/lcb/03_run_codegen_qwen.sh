#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_common_run_env.sh"
ensure_lcb_root
print_run_config
python "$SCRIPT_DIR/02b_patch_vllm_max_model_len.py" .

python -m lcb_runner.runner.main \
  --model "Qwen/Qwen2.5-Coder-7B-Instruct" \
  --scenario codegeneration \
  --evaluate \
  --release_version "$RELEASE_VERSION" \
  --start_date "$START_DATE" \
  --end_date "$END_DATE" \
  --n "$N" \
  --temperature "$TEMPERATURE" \
  --top_p "$TOP_P" \
  --max_tokens "$MAX_TOKENS" \
  --tensor_parallel_size "$TENSOR_PARALLEL_SIZE" \
  --dtype "$DTYPE" \
  --timeout "$TIMEOUT" \
  --num_process_evaluate "$NUM_PROCESS_EVALUATE" \
  --cache_batch_size "$CACHE_BATCH_SIZE" \
  --use_cache \
  $SMOKE_FLAG
