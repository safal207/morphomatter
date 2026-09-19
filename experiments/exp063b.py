"""Run 063B from the repository root; no tuning on evaluation worlds.

python -m experiments.exp063b --stage evaluation --output out/exp063b --replay
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time
import zipfile

from experiments.exp063 import bootstrap, source_fingerprint, write_json
from morphomatter.exp063 import digest, load_manifest
from morphomatter.exp063b import POLICIES, make_scoped_world, run_guarded

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = (
    "morphomatter/__init__.py", "morphomatter/exp063.py", "morphomatter/exp063b.py",
    "experiments/exp063.py", "experiments/exp063b.py", "experiments/exp063_manifest.json",
    "experiments/exp063b_manifest.json", "tests/test_exp063.py", "tests/test_exp063b.py",
    ".github/workflows/exp063b.yml",
)
LEGACY_SOURCE_HASH = "00ca001fc114d63e2e1b793f4195ff2609b3607e69ae8d774136c70e7f0c1ef3"


def read_protocol() -> dict:
    m = json.loads((ROOT / "experiments/exp063b_manifest.json").read_text())
    if m["version"] != "063b-pair-v1":
        raise ValueError("Unsupported 063B protocol")
    if digest(load_manifest()) != m["base_manifest_sha256"] or source_fingerprint() != LEGACY_SOURCE_HASH:
        raise ValueError("ARCHIVED_063_BASELINE_CHANGED")
    if set(m["policies"]) != set(POLICIES):
        raise ValueError("Policy vocabulary mismatch")
    return m


def aggregate(rows: list[dict]) -> dict:
    metrics = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        metrics[policy] = {
            "worlds": len(subset), "total_loss": sum(r["loss"] for r in subset),
            "mean_loss": statistics.fmean(r["loss"] for r in subset),
            "correct_decisions": sum(r["correct"] for r in subset),
            "wrong_decisions": sum(r["wrong"] for r in subset),
            "withheld_decisions": sum(r["hold"] for r in subset),
            "mean_spent": statistics.fmean(r["spent"] for r in subset),
            "pair_selections": sum(r["pair_selections"] for r in subset),
            "known_invalid_leakage": sum(r["known_invalid_leakage"] for r in subset),
            "receipt_rejections": sum(r["receipt_rejections"] for r in subset),
            "budget_violations": sum(r["budget_violation"] for r in subset),
            "invalid_chains": sum(not r["ledger_chain_valid"] for r in subset),
        }
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("smoke", "evaluation"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    m = read_protocol()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    seeds = (list(range(m["evaluation_seeds"]["start"], m["evaluation_seeds"]["stop_exclusive"]))
             if args.stage == "evaluation" else m["smoke_worlds"])
    prior = m["excluded_prior_evaluation_seeds"]
    if any(prior["start"] <= s < prior["stop_exclusive"] for s in seeds):
        raise ValueError("Evaluation-world overlap with pilot v1")
    hashes = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCE_FILES}
    source_hash = digest(hashes)
    write_json(output / "source_hashes.json", hashes)
    write_json(output / "manifest.json", m)
    # Ship an exact tracked-source archive without credentials or untracked outputs.
    subprocess.run(["git", "archive", "--format=zip", "--output=" + str(output / "source_snapshot.zip"),
                    "HEAD"], cwd=ROOT, check=True)
    timings = {policy: 0.0 for policy in POLICIES}
    rows = []
    replay_failures = 0
    trace_hash = sha256()
    start = time.perf_counter()
    with (output / "records.jsonl").open("w", encoding="utf-8") as stream:
        for index, seed in enumerate(seeds):
            world = make_scoped_world(seed)
            for policy in POLICIES:
                tick = time.perf_counter()
                row = run_guarded(world, policy, m["budget"], m["maximum_steps"])
                timings[policy] += time.perf_counter() - tick
                if args.replay:
                    repeat = run_guarded(world, policy, m["budget"], m["maximum_steps"])
                    replay_failures += int(row != repeat)
                encoded = json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
                stream.write(encoded)
                trace_hash.update(encoded.encode())
                rows.append({k: v for k, v in row.items() if k not in ("decisions", "verification_events", "ledger")})
            if (index + 1) % 32 == 0:
                print(f"Completed {index + 1}/{len(seeds)} worlds", flush=True)
    metrics = aggregate(rows)
    violations = sum(v[k] for v in metrics.values() for k in
                     ("known_invalid_leakage", "receipt_rejections", "budget_violations", "invalid_chains"))
    summary = {
        "experiment": "063B", "version": m["version"], "stage": args.stage,
        "scope": "FINITE_DIAGNOSTIC_PAIR_LOOKAHEAD_NOT_MATERIAL_PHYSICS",
        "code_commit": os.environ.get("CODE_COMMIT", "UNSPECIFIED_LOCAL_COMMIT"),
        "base_commit": m["base_commit"], "legacy_source_sha256": LEGACY_SOURCE_HASH,
        "source_sha256": source_hash, "protocol_sha256": digest(m),
        "world_seeds": seeds, "metrics": metrics, "replay_checked": args.replay,
        "replay_failures": replay_failures if args.replay else None,
        "records_sha256": trace_hash.hexdigest(), "integrity_violations": violations,
        "comparisons": {},
    }
    if args.stage == "evaluation":
        keyed = {(r["world_id"], r["policy"]): r for r in rows}
        for role, comparator in (("primary", m["primary_comparator"]),
                                 ("secondary_descriptive", m["secondary_comparator"])):
            differences = [keyed[(seed, comparator)]["loss"] - keyed[(seed, "pair_value")]["loss"]
                           for seed in seeds]
            ci = bootstrap(differences, m["bootstrap"]["resamples"], m["bootstrap"]["seed"])
            summary["comparisons"][role] = {
                "comparator": comparator, "candidate": "pair_value",
                "mean_loss_reduction": statistics.fmean(differences),
                "paired_world_bootstrap_95_interval": ci,
                "no_higher_wrong_count": metrics["pair_value"]["wrong_decisions"] <= metrics[comparator]["wrong_decisions"],
                "worlds_better": sum(x > 0 for x in differences),
                "worlds_equal": sum(x == 0 for x in differences),
                "worlds_worse": sum(x < 0 for x in differences),
            }
        primary = summary["comparisons"]["primary"]
        gain = (primary["paired_world_bootstrap_95_interval"][0] > 0 and primary["no_higher_wrong_count"]
                and violations == 0 and replay_failures == 0)
        summary["label"] = ("INTEGRITY_FAILED" if violations or replay_failures else
                            "BOUNDED_PAIR_LOOKAHEAD_GAIN" if gain else "PAIR_LOOKAHEAD_MIXED_OR_NO_GAIN")
    else:
        summary["label"] = "SMOKE_ONLY_NO_SCIENTIFIC_VERDICT"
    write_json(output / "summary.json", summary)
    write_json(output / "endpoints.json", rows)
    write_json(output / "runtime.json", {
        "seconds_including_replay": time.perf_counter() - start,
        "policy_seconds_excluding_replay": timings,
        "python": platform.python_version(), "platform": platform.platform(),
        "note": "Single-run runtime, not physical energy or an asymptotic guarantee",
    })
    print("SUMMARY=" + json.dumps(summary, sort_keys=True), flush=True)
    if violations or replay_failures:
        raise SystemExit("Integrity gate failed; a null scientific result does not fail CI")


if __name__ == "__main__":
    main()
