#!/usr/bin/env bash
set -euo pipefail
# Run from inside the LiveCodeBench repo after 01_setup_lcb.sh.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/03_run_codegen_qwen.sh"
bash "$SCRIPT_DIR/04_run_codegen_deepseek.sh"
bash "$SCRIPT_DIR/05_run_selfrepair_qwen.sh"
bash "$SCRIPT_DIR/06_run_selfrepair_deepseek.sh"
bash "$SCRIPT_DIR/08_collect_results.sh"
