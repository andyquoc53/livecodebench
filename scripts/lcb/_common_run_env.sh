#!/usr/bin/env bash
# Shared environment defaults for LiveCodeBench runs.

RELEASE_VERSION="${RELEASE_VERSION:-release_v5}"
START_DATE="${START_DATE:-2024-08-01}"
END_DATE="${END_DATE:-2025-01-31}"
N="${N:-1}"
TEMPERATURE="${TEMPERATURE:-0.2}"
MAX_TOKENS="${MAX_TOKENS:-4096}"
TIMEOUT="${TIMEOUT:-10}"
NUM_PROCESS_EVALUATE="${NUM_PROCESS_EVALUATE:-4}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-1}"
DTYPE="${DTYPE:-bfloat16}"
TOP_P="${TOP_P:-0.95}"
LCB_MAX_MODEL_LEN="${LCB_MAX_MODEL_LEN:-8192}"
VLLM_GPU_MEMORY_UTILIZATION="${VLLM_GPU_MEMORY_UTILIZATION:-0.90}"
CACHE_BATCH_SIZE="${CACHE_BATCH_SIZE:-25}"
TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
VLLM_WORKER_MULTIPROC_METHOD="${VLLM_WORKER_MULTIPROC_METHOD:-spawn}"
ANTHROPIC_KEY="${ANTHROPIC_KEY:-${ANTHROPIC_API_KEY:-}}"

if [[ -d "/workspace" ]]; then
  HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
  HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-1}"
fi

export LCB_MAX_MODEL_LEN
export VLLM_GPU_MEMORY_UTILIZATION
export TOKENIZERS_PARALLELISM
export PYTORCH_CUDA_ALLOC_CONF
export VLLM_WORKER_MULTIPROC_METHOD
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-0}"
export ANTHROPIC_KEY

SMOKE_FLAG=""
if [[ "${SMOKE:-0}" == "1" ]]; then
  SMOKE_FLAG="--debug"
fi

ensure_lcb_root() {
  if [[ ! -f "pyproject.toml" || ! -d "lcb_runner" ]]; then
    echo "ERROR: Run this script from the root of the official LiveCodeBench repository." >&2
    exit 1
  fi
  if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
}

print_run_config() {
  echo "Release:              $RELEASE_VERSION"
  echo "Date window:          $START_DATE to $END_DATE"
  echo "n / temperature:      $N / $TEMPERATURE"
  echo "max_tokens:           $MAX_TOKENS"
  echo "timeout:              $TIMEOUT"
  echo "eval processes:       $NUM_PROCESS_EVALUATE"
  echo "tensor parallel size: $TENSOR_PARALLEL_SIZE"
  echo "dtype:                $DTYPE"
  echo "smoke/debug:          ${SMOKE:-0}"
  echo "LCB max model len:    $LCB_MAX_MODEL_LEN"
  echo "vLLM GPU memory util: $VLLM_GPU_MEMORY_UTILIZATION"
  echo "HF cache:             $HF_HOME"
}
