#!/usr/bin/env python3
"""Summarize LiveCodeBench output JSON files into report-ready CSV/Markdown.

The script is intentionally tolerant because LiveCodeBench output formats can
change across commits. It searches for *_eval.json and *_eval_all.json under
output/, extracts overall metrics, and builds per-instance breakdowns by model,
scenario, difficulty, platform, and contest month.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


IMPORTANT_SUMMARY_KEYS = [
    "model_dir",
    "scenario",
    "guessed_pass@1",
    "computed_first_sample_pass_rate",
    "computed_first_sample_n",
    "num_instances",
    "eval_json",
    "eval_all_json",
]

INSTANCE_KEYS = [
    "model_dir",
    "scenario",
    "question_id",
    "question_title",
    "platform",
    "difficulty",
    "contest_date",
    "contest_month",
    "pass_at_1",
    "first_sample_passed",
    "num_samples",
]

GROUP_KEYS = ["model_dir", "scenario", "group_type", "group_value", "n", "pass_at_1"]
REPAIR_KEYS = [
    "model_dir",
    "group_type",
    "group_value",
    "n",
    "codegeneration_pass_at_1",
    "selfrepair_pass_at_1",
    "repair_gain",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_numbers(obj: Any, prefix: str = "") -> Iterable[tuple[str, float]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            yield from iter_numbers(v, key)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_numbers(v, f"{prefix}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool) and math.isfinite(float(obj)):
        yield prefix, float(obj)


def guess_metric(summary_obj: Any) -> dict[str, float | str]:
    nums = list(iter_numbers(summary_obj))
    out: dict[str, float | str] = {}

    for k, v in nums:
        kl = k.lower()
        if any(tok in kl for tok in ["pass", "repair", "score", "accuracy"]):
            out[k] = v

    for k, v in nums:
        kl = k.lower().replace("_", "").replace("@", "")
        if "pass1" in kl or "passat1" in kl or "pass@1" in k.lower():
            out.setdefault("guessed_pass@1", v)
            break
    return out


def first_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    if isinstance(value, dict):
        for key in ["passed", "correct", "success"]:
            if key in value:
                return first_bool(value[key])
    return None


def graded_values(item: dict[str, Any]) -> list[bool]:
    for key in ["graded_list", "graded", "pass_list"]:
        value = item.get(key)
        if isinstance(value, list):
            out = []
            for entry in value:
                parsed = first_bool(entry)
                if parsed is not None:
                    out.append(parsed)
            if out:
                return out

    for key in ["passed", "correct", "success", "eval"]:
        parsed = first_bool(item.get(key))
        if parsed is not None:
            return [parsed]
    return []


def scenario_from_filename(path: Path) -> str:
    name = path.name
    if name.endswith("_eval_all.json"):
        name = name[: -len("_eval_all.json")]
    elif name.endswith("_eval.json"):
        name = name[: -len("_eval.json")]
    return name.split("_", 1)[0]


def contest_month(contest_date: str) -> str:
    if not contest_date:
        return ""
    try:
        return datetime.fromisoformat(contest_date).strftime("%Y-%m")
    except ValueError:
        return contest_date[:7]


def eval_all_stats(eval_all: Any) -> dict[str, Any]:
    if not isinstance(eval_all, list):
        return {"num_instances": ""}

    pass_values = []
    for item in eval_all:
        if isinstance(item, dict):
            graded = graded_values(item)
            if graded:
                pass_values.append(graded[0])

    stats: dict[str, Any] = {"num_instances": len(eval_all)}
    if pass_values:
        stats["computed_first_sample_pass_rate"] = sum(pass_values) / len(pass_values)
        stats["computed_first_sample_n"] = len(pass_values)
    return stats


def instance_rows(model_dir: str, scenario: str, eval_all: Any) -> list[dict[str, Any]]:
    if not isinstance(eval_all, list):
        return []

    rows = []
    for item in eval_all:
        if not isinstance(item, dict):
            continue
        graded = graded_values(item)
        contest_date = item.get("contest_date", "")
        first_passed = graded[0] if graded else ""
        pass_at_1 = item.get("pass@1")
        if pass_at_1 is None and graded:
            pass_at_1 = sum(graded) / len(graded)

        rows.append(
            {
                "model_dir": model_dir,
                "scenario": scenario,
                "question_id": item.get("question_id", ""),
                "question_title": item.get("question_title", ""),
                "platform": item.get("platform", ""),
                "difficulty": item.get("difficulty", ""),
                "contest_date": contest_date,
                "contest_month": contest_month(str(contest_date)),
                "pass_at_1": pass_at_1 if pass_at_1 is not None else "",
                "first_sample_passed": first_passed,
                "num_samples": len(graded) if graded else "",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_keys: list[str]) -> None:
    keys = [k for k in preferred_keys if any(k in r for r in rows)]
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def rate(rows: list[dict[str, Any]]) -> float | str:
    vals = [r["first_sample_passed"] for r in rows if isinstance(r.get("first_sample_passed"), bool)]
    if not vals:
        return ""
    return sum(vals) / len(vals)


def breakdown_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        keys = [
            ("overall", "all"),
            ("difficulty", str(row.get("difficulty", ""))),
            ("platform", str(row.get("platform", ""))),
            ("contest_month", str(row.get("contest_month", ""))),
        ]
        for group_type, group_value in keys:
            if group_value:
                grouped[(row["model_dir"], row["scenario"], group_type, group_value)].append(row)

    out = []
    for (model_dir, scenario, group_type, group_value), group_rows in sorted(grouped.items()):
        out.append(
            {
                "model_dir": model_dir,
                "scenario": scenario,
                "group_type": group_type,
                "group_value": group_value,
                "n": len(group_rows),
                "pass_at_1": rate(group_rows),
            }
        )
    return out


def repair_gain_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_model_scenario: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model_scenario[(row["model_dir"], row["scenario"])].append(row)

    out = []
    for model_dir in sorted({row["model_dir"] for row in rows}):
        codegen = by_model_scenario.get((model_dir, "codegeneration"), [])
        repair = by_model_scenario.get((model_dir, "selfrepair"), [])
        if not codegen or not repair:
            continue

        for group_type in ["overall", "difficulty", "platform", "contest_month"]:
            if group_type == "overall":
                group_values = ["all"]
            else:
                group_values = sorted(
                    {
                        str(row.get(group_type, ""))
                        for row in codegen + repair
                        if str(row.get(group_type, ""))
                    }
                )
            for group_value in group_values:
                if group_type == "overall":
                    cg_rows = codegen
                    sr_rows = repair
                else:
                    cg_rows = [r for r in codegen if str(r.get(group_type, "")) == group_value]
                    sr_rows = [r for r in repair if str(r.get(group_type, "")) == group_value]
                if not cg_rows or not sr_rows:
                    continue
                cg_rate = rate(cg_rows)
                sr_rate = rate(sr_rows)
                gain = sr_rate - cg_rate if isinstance(cg_rate, float) and isinstance(sr_rate, float) else ""
                out.append(
                    {
                        "model_dir": model_dir,
                        "group_type": group_type,
                        "group_value": group_value,
                        "n": min(len(cg_rows), len(sr_rows)),
                        "codegeneration_pass_at_1": cg_rate,
                        "selfrepair_pass_at_1": sr_rate,
                        "repair_gain": gain,
                    }
                )
    return out


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_markdown(path: Path, summary_rows: list[dict[str, Any]], repair_rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("# LiveCodeBench run summary\n\n")
        if not summary_rows:
            f.write("No `*_eval.json` files found.\n")
            return

        f.write("## Overall\n\n")
        f.write("| model | scenario | pass@1 | computed pass rate | n |\n")
        f.write("|---|---:|---:|---:|---:|\n")
        for row in summary_rows:
            f.write(
                f"| {row.get('model_dir','')} | {row.get('scenario','')} | "
                f"{fmt(row.get('guessed_pass@1',''))} | {fmt(row.get('computed_first_sample_pass_rate',''))} | "
                f"{row.get('num_instances','')} |\n"
            )

        if repair_rows:
            f.write("\n## Self-Repair Gain\n\n")
            f.write("| model | group | codegen pass@1 | repair pass@1 | gain | n |\n")
            f.write("|---|---:|---:|---:|---:|---:|\n")
            for row in repair_rows:
                if row["group_type"] != "overall":
                    continue
                f.write(
                    f"| {row['model_dir']} | {row['group_value']} | "
                    f"{fmt(row['codegeneration_pass_at_1'])} | {fmt(row['selfrepair_pass_at_1'])} | "
                    f"{fmt(row['repair_gain'])} | {row['n']} |\n"
                )

        f.write("\nGenerated files:\n\n")
        f.write("- `lcb_summary.csv`: overall metric extraction\n")
        f.write("- `lcb_by_instance.csv`: one row per benchmark problem\n")
        f.write("- `lcb_breakdown.csv`: grouped results for report tables\n")
        f.write("- `lcb_repair_gain.csv`: self-repair improvement over initial code generation\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output_dir", type=Path, default=Path("output"))
    ap.add_argument("--out_dir", type=Path, default=Path("run_summaries"))
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, Any]] = []
    all_instances: list[dict[str, Any]] = []

    for eval_path in sorted(args.output_dir.rglob("*_eval.json")):
        if eval_path.name.endswith("_eval_all.json"):
            continue
        rel = eval_path.relative_to(args.output_dir)
        model_dir = rel.parts[0] if rel.parts else "unknown"
        scenario = scenario_from_filename(eval_path)
        row: dict[str, Any] = {
            "model_dir": model_dir,
            "scenario": scenario,
            "eval_json": str(eval_path),
        }
        try:
            row.update(guess_metric(load_json(eval_path)))
        except Exception as e:
            row["error_eval_json"] = repr(e)

        eval_all_path = eval_path.with_name(eval_path.name.replace("_eval.json", "_eval_all.json"))
        if eval_all_path.exists():
            row["eval_all_json"] = str(eval_all_path)
            try:
                eval_all = load_json(eval_all_path)
                row.update(eval_all_stats(eval_all))
                all_instances.extend(instance_rows(model_dir, scenario, eval_all))
            except Exception as e:
                row["error_eval_all_json"] = repr(e)
        summary_rows.append(row)

    breakdown = breakdown_rows(all_instances)
    repair_gain = repair_gain_rows(all_instances)

    write_csv(args.out_dir / "lcb_summary.csv", summary_rows, IMPORTANT_SUMMARY_KEYS)
    write_csv(args.out_dir / "lcb_by_instance.csv", all_instances, INSTANCE_KEYS)
    write_csv(args.out_dir / "lcb_breakdown.csv", breakdown, GROUP_KEYS)
    write_csv(args.out_dir / "lcb_repair_gain.csv", repair_gain, REPAIR_KEYS)
    write_markdown(args.out_dir / "lcb_summary.md", summary_rows, repair_gain)

    print(f"Wrote {args.out_dir / 'lcb_summary.csv'}")
    print(f"Wrote {args.out_dir / 'lcb_by_instance.csv'}")
    print(f"Wrote {args.out_dir / 'lcb_breakdown.csv'}")
    print(f"Wrote {args.out_dir / 'lcb_repair_gain.csv'}")
    print(f"Wrote {args.out_dir / 'lcb_summary.md'}")


if __name__ == "__main__":
    main()
