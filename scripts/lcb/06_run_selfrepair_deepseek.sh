#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_common_run_env.sh"
ensure_lcb_root
print_run_config
python "$SCRIPT_DIR/02b_patch_vllm_max_model_len.py" .
python "$SCRIPT_DIR/02c_patch_selfrepair_date_filter.py" .
python "$SCRIPT_DIR/02g_patch_selfrepair_styles.py" .

python "$SCRIPT_DIR/02_patch_deepseek_v2_lite.py" .

# Self-repair requires the matching codegeneration_{N}_{TEMPERATURE}_eval_all.json from the codegen run.
python -m lcb_runner.runner.main \
  --model "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct" \
  --scenario selfrepair \
  --evaluate \
  --release_version "$RELEASE_VERSION" \
  --start_date "$START_DATE" \
  --end_date "$END_DATE" \
  --codegen_n "$N" \
  --n 1 \
  --temperature "$TEMPERATURE" \
  --top_p "$TOP_P" \
  --max_tokens "$MAX_TOKENS" \
  --tensor_parallel_size "$TENSOR_PARALLEL_SIZE" \
  --dtype "$DTYPE" \
  --timeout "$TIMEOUT" \
  --num_process_evaluate "$NUM_PROCESS_EVALUATE" \
  --cache_batch_size "$CACHE_BATCH_SIZE" \
  --trust_remote_code \
  --use_cache \
  $SMOKE_FLAG
