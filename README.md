# LCB Progress Survey Code Package

This repository accompanies the report:

**Survey: Measuring Algorithmic Progress in Modern LLMs on Competitive Programming via LiveCodeBench**

It is intentionally separate from the original LiveCodeBench repository. It contains:

- `data/`: small background CSV files used for proposal/report figures.
- `scripts/make_figures.py`: recreates the report figures from the CSV files.
- `scripts/run_lcb_experiments.sh`: a Vast.ai/A100-ready wrapper for running LiveCodeBench code generation and self-repair.
- `scripts/lcb/`: patched helper scripts for Qwen2.5-Coder-7B-Instruct, DeepSeek-Coder-V2-Lite-Instruct, and Claude Sonnet 4.6 API runs.
- `notebooks/LiveCodeBench_Qwen_DeepSeek_Run.ipynb`: the notebook workflow for Vast.ai, Colab, or plain Jupyter.
- `requirements.txt`: Python packages for the lightweight analysis scripts.

## What was actually executed

The final report is based on a controlled LiveCodeBench `release_v5` run on the proposal-aligned date window `2024-08-01` through `2025-01-31`. Published LiveCodeBench and model-report measurements are used only as background context.

After GPU/API setup on Vast.ai, the repository scripts were executed against the official LiveCodeBench runner for the full filtered 279-problem window.

Executed run artifacts are tracked under `results/livecodebench/`:

- Claude Sonnet 4.6 code generation/self-repair: 279 problems, pass@1 = 0.6631 / 0.6989.
- Qwen2.5-Coder-7B-Instruct code generation/self-repair: 279 problems, pass@1 = 0.1756 / 0.1756.
- DeepSeek-Coder-V2-Lite-Instruct code generation/self-repair: 279 problems, pass@1 = 0.1756 / 0.1900.

All three model rows above use the same filtered LiveCodeBench window. Earlier 15-problem smoke checks and the initial 100-problem Sonnet sample were superseded by these full filtered-window runs.

Qwen and DeepSeek are run as regular instruct/code models through vLLM. They are not QwQ/DeepSeek-R1-style reasoning models, and the scripts do not enable any extended-thinking mode.

## Executed LiveCodeBench summaries

The real runner outputs were summarized with `scripts/lcb/08_collect_results.sh`. The tracked summary files are:

- `results/livecodebench/lcb_summary.md`
- `results/livecodebench/lcb_summary.csv`
- `results/livecodebench/lcb_by_instance.csv`
- `results/livecodebench/lcb_breakdown.csv`
- `results/livecodebench/lcb_repair_gain.csv`

The raw archive from Vast.ai was `lcb_run_outputs.zip`. It is intentionally ignored by Git because the repository tracks the smaller, reviewable CSV/Markdown summaries instead.

## Recreate the report figures

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/make_figures.py --data_dir data --out_dir figures
```

The script creates the following figures:

- `release_growth.pdf`
- `open_model_lcb.pdf`
- `difficulty_split.pdf`
- `repair_gain.pdf`

## Prospective LiveCodeBench execution

Clone and install the official LiveCodeBench runner:

```bash
git clone https://github.com/LiveCodeBench/LiveCodeBench.git
cd LiveCodeBench
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e .
```

Then run the wrapper from inside the cloned LiveCodeBench repository:

```bash
bash /path/to/this_repo/scripts/run_lcb_experiments.sh
```

Recommended controlled window for the proposal:

- `--release_version release_v5`
- `--start_date 2024-08-01`
- `--end_date 2025-01-31`

For a 2026 final run, `release_v6` can also be used if every model is evaluated on the same date window.

For a quick smoke test before spending full GPU time:

```bash
SMOKE=1 bash /path/to/this_repo/scripts/run_lcb_experiments.sh
```

## Claude Sonnet 4.6 API runs

The Sonnet path is intentionally separate from the open-model runner so paid API calls can be capped for debugging or expanded for the full filtered run. It uses the non-thinking Claude style in LiveCodeBench and defaults to 100 problems.

```bash
export ANTHROPIC_KEY="sk-ant-..."
# or export ANTHROPIC_API_KEY="sk-ant-..."

cd /path/to/LiveCodeBench
bash /path/to/this_repo/scripts/lcb/01_setup_lcb.sh
API_SAMPLE_SIZE=100 SONNET_MAX_TOKENS=4096 bash /path/to/this_repo/scripts/lcb/10_run_codegen_sonnet_sample.sh
```

Optional self-repair run, after the code-generation run:

```bash
API_SAMPLE_SIZE=100 SONNET_MAX_TOKENS=4096 bash /path/to/this_repo/scripts/lcb/11_run_selfrepair_sonnet_sample.sh
```

To evaluate Claude Sonnet 4.6 on the full filtered date window instead of the
100-problem cap, use `API_SAMPLE_SIZE=all` or `SONNET_FULL_RUN=1`:

```bash
API_SAMPLE_SIZE=all SONNET_MAX_TOKENS=4096 bash /path/to/this_repo/scripts/lcb/10_run_codegen_sonnet_sample.sh
API_SAMPLE_SIZE=all SONNET_MAX_TOKENS=4096 bash /path/to/this_repo/scripts/lcb/11_run_selfrepair_sonnet_sample.sh
```

The wrapper applies three compatibility patches to the official LiveCodeBench checkout:

- adds `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` and `claude-sonnet-4-6` to `lm_styles.py` when missing;
- caps vLLM context and GPU memory usage through `LCB_MAX_MODEL_LEN` and `VLLM_GPU_MEMORY_UTILIZATION`;
- makes self-repair respect the same `--start_date` and `--end_date` filter as code generation.
- makes LiveCodeBench `--debug` respect `LCB_DEBUG_LIMIT` for safe API sampling.

## GitHub repository

Repository URL:

```text
https://github.com/andyquoc53/livecodebench
```
