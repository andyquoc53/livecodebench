#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/_common_run_env.sh"
ensure_lcb_root

if [[ -z "${ANTHROPIC_KEY:-}" ]]; then
  echo "ERROR: set ANTHROPIC_KEY or ANTHROPIC_API_KEY before running the Sonnet API run." >&2
  exit 1
fi

API_SAMPLE_SIZE="${API_SAMPLE_SIZE:-100}"
SONNET_MAX_TOKENS="${SONNET_MAX_TOKENS:-2048}"
ANTHROPIC_MULTIPROCESS="${ANTHROPIC_MULTIPROCESS:-1}"
export LCB_DEBUG_LIMIT="$API_SAMPLE_SIZE"

print_run_config
echo "Sonnet model:         claude-sonnet-4-6"
echo "API problem count:    $API_SAMPLE_SIZE"
echo "Sonnet max tokens:    $SONNET_MAX_TOKENS"
echo "API multiprocess:     $ANTHROPIC_MULTIPROCESS"

python "$SCRIPT_DIR/02c_patch_selfrepair_date_filter.py" .
python "$SCRIPT_DIR/02d_patch_claude_sonnet_4_6.py" .
python "$SCRIPT_DIR/02e_patch_debug_sample_limit.py" .

# Self-repair requires the matching Sonnet codegeneration_1_<temperature>_eval_all.json.
python -m lcb_runner.runner.main \
  --model "claude-sonnet-4-6" \
  --scenario selfrepair \
  --evaluate \
  --release_version "$RELEASE_VERSION" \
  --start_date "$START_DATE" \
  --end_date "$END_DATE" \
  --codegen_n 1 \
  --n 1 \
  --temperature "$TEMPERATURE" \
  --top_p "$TOP_P" \
  --max_tokens "$SONNET_MAX_TOKENS" \
  --multiprocess "$ANTHROPIC_MULTIPROCESS" \
  --timeout "$TIMEOUT" \
  --num_process_evaluate "$NUM_PROCESS_EVALUATE" \
  --use_cache \
  --debug
