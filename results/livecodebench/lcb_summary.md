# LiveCodeBench run summary

## Overall

| model | scenario | pass@1 | computed pass rate | n |
|---|---:|---:|---:|---:|
| Claude-Sonnet-4.6 | Scenario.codegeneration | 0.8600 | 0.8600 | 100 |
| Claude-Sonnet-4.6 | Scenario.selfrepair | 0.8600 | 0.8600 | 100 |
| DeepSeek-Coder-V2-Lite-Instruct | Scenario.codegeneration | 0.0000 | 0.0000 | 15 |
| DeepSeek-Coder-V2-Lite-Instruct | Scenario.selfrepair | 0.0667 | 0.0667 | 15 |
| Qwen2.5-Coder-Ins-7B | Scenario.codegeneration | 0.0667 | 0.0667 | 15 |
| Qwen2.5-Coder-Ins-7B | Scenario.selfrepair | 0.0667 | 0.0667 | 15 |

Generated files:

- `lcb_summary.csv`: overall metric extraction
- `lcb_by_instance.csv`: one row per benchmark problem
- `lcb_breakdown.csv`: grouped results for report tables
- `lcb_repair_gain.csv`: self-repair improvement over initial code generation
