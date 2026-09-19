"""Run from repository root: python -m experiments.exp063 --stage smoke --output out.

Development emits a comparator lock. Evaluation refuses a missing/stale lock.
A pilot result is not completion of the broader Experiment 063 protocol.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import statistics
import time

from morphomatter.exp063 import POLICIES, digest, load_manifest, make_world, run_policy

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = ("morphomatter/__init__.py", "morphomatter/exp063.py",
                "experiments/exp063.py", "tests/test_exp063.py")


def source_fingerprint() -> str:
    return digest({name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES})


def write_json(path: Path, value: object) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (index - low)


def bootstrap(differences: list[float], count: int, seed: int) -> list[float]:
    if not differences or count < 1:
        raise ValueError("Bootstrap needs data and positive resample count")
    rng = random.Random(seed)
    means = [statistics.fmean(rng.choices(differences, k=len(differences))) for _ in range(count)]
    return [quantile(means, 0.025), quantile(means, 0.975)]


def summarize(rows: list[dict]) -> dict:
    result = {}
    for policy in POLICIES:
        subset = [r for r in rows if r["policy"] == policy]
        result[policy] = {
            "worlds": len(subset),
            "mean_loss": statistics.fmean(r["loss"] for r in subset),
            "total_loss": sum(r["loss"] for r in subset),
            "mean_spent": statistics.fmean(r["spent"] for r in subset),
            "correct_decisions": sum(r["correct"] for r in subset),
            "wrong_decisions": sum(r["wrong"] for r in subset),
            "withheld_decisions": sum(r["hold"] for r in subset),
            "known_invalid_leakage": sum(r["known_invalid_leakage"] for r in subset),
            "budget_violations": sum(r["budget_violation"] for r in subset),
            "invalid_ledger_chains": sum(not r["ledger_chain_valid"] for r in subset),
        }
    return result


def validate_lock(lock: dict, manifest: dict, fingerprint: str) -> str:
    if lock.get("source_sha256") != fingerprint or lock.get("manifest_sha256") != digest(manifest):
        raise ValueError("STALE_COMPARATOR_LOCK: code or manifest changed")
    if lock.get("development_seeds") != manifest["development_seeds"]:
        raise ValueError("Comparator was not selected on the declared development split")
    selected = lock.get("selected_policy")
    if selected not in manifest["comparator_candidates"]:
        raise ValueError("Invalid frozen comparator")
    metrics = lock.get("development_metrics", {})
    expected = min(manifest["comparator_candidates"], key=lambda p: (metrics[p]["mean_loss"], p))
    if selected != expected:
        raise ValueError("Comparator does not match the frozen selection rule")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("smoke", "development", "evaluation"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lock", type=Path)
    parser.add_argument("--replay", action="store_true", help="Run each policy/world twice and compare full records")
    args = parser.parse_args()
    manifest = load_manifest()
    fingerprint = source_fingerprint()
    comparator = None
    lock = None
    if args.stage == "evaluation":
        if args.lock is None:
            parser.error("Evaluation requires --lock from development, frozen before evaluation")
        lock = json.loads(args.lock.read_text(encoding="utf-8"))
        comparator = validate_lock(lock, manifest, fingerprint)
        interval = manifest["evaluation_seeds"]
    elif args.stage == "development":
        interval = manifest["development_seeds"]
    else:
        interval = {"start": 0, "stop_exclusive": 3}
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    replay_failures = 0
    timings = {p: 0.0 for p in POLICIES}
    started = time.perf_counter()
    records_hash = sha256()
    with (args.output / "records.jsonl").open("w", encoding="utf-8") as records:
        for seed in range(interval["start"], interval["stop_exclusive"]):
            world = make_world(seed, manifest)
            for policy in POLICIES:
                tick = time.perf_counter()
                row = run_policy(world, policy, manifest["budget"], manifest["maximum_steps"])
                timings[policy] += time.perf_counter() - tick
                if args.replay:
                    repeat = run_policy(world, policy, manifest["budget"], manifest["maximum_steps"])
                    replay_failures += int(row != repeat)
                encoded = json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
                records.write(encoded)
                records_hash.update(encoded.encode())
                # Full evidence is streamed to JSONL; aggregate keeps only endpoints.
                rows.append({k: v for k, v in row.items() if k not in ("decisions", "verification_events", "ledger")})
    metrics = summarize(rows)
    summary = {
        "experiment": "063", "version": manifest["version"], "stage": args.stage,
        "scope": "PILOT_ONLY_NOT_FULL_063_CONFIRMATORY_RESULT",
        "code_commit": os.environ.get("CODE_COMMIT", "UNSPECIFIED_LOCAL_COMMIT"),
        "source_sha256": fingerprint, "manifest_sha256": digest(manifest),
        "world_seeds": interval, "metrics": metrics,
        "records_sha256": records_hash.hexdigest(),
        "replay_checked": args.replay,
        "replay_failures": replay_failures if args.replay else None,
    }
    if args.stage == "development":
        comparator = min(manifest["comparator_candidates"], key=lambda p: (metrics[p]["mean_loss"], p))
        lock = {
            "version": manifest["version"], "selected_policy": comparator,
            "development_seeds": interval, "source_sha256": fingerprint,
            "manifest_sha256": digest(manifest), "development_metrics": metrics,
            "development_records_sha256": records_hash.hexdigest(),
            "development_code_commit": summary["code_commit"],
        }
        write_json(args.output / "comparator_lock.json", lock)
        summary["selected_comparator"] = comparator
        print("COMPARATOR_LOCK=" + json.dumps(lock, sort_keys=True))
    if args.stage == "evaluation":
        by_key = {(r["world_id"], r["policy"]): r for r in rows}
        differences = [by_key[(s, comparator)]["loss"] - by_key[(s, "decision_value")]["loss"]
                       for s in range(interval["start"], interval["stop_exclusive"])]
        ci = bootstrap(differences, manifest["bootstrap"]["resamples"], manifest["bootstrap"]["seed"])
        candidate = metrics["decision_value"]
        violations = sum(m["known_invalid_leakage"] + m["budget_violations"] + m["invalid_ledger_chains"]
                         for m in metrics.values())
        gain = (ci[0] > 0 and violations == 0 and replay_failures == 0 and
                candidate["wrong_decisions"] <= metrics[comparator]["wrong_decisions"])
        summary["primary"] = {
            "comparator": comparator, "mean_paired_loss_reduction": statistics.fmean(differences),
            "paired_bootstrap_95_interval": ci,
            "no_higher_observed_wrong_count": candidate["wrong_decisions"] <= metrics[comparator]["wrong_decisions"],
            "label": "PILOT_DECISION_VALUE_GAIN" if gain else "PILOT_MIXED_OR_NO_GAIN",
            "comparator_lock_sha256": digest(lock),
        }
    write_json(args.output / "summary.json", summary)
    write_json(args.output / "endpoints.json", rows)
    write_json(args.output / "runtime.json", {
        "seconds_including_replay": time.perf_counter() - started,
        "policy_seconds_excluding_replay": timings,
        "python": platform.python_version(), "platform": platform.platform(),
        "note": "Observed runtime is not a physical energy measurement or an algorithmic guarantee",
    })
    print("SUMMARY=" + json.dumps(summary, sort_keys=True))
    if replay_failures or any(m["known_invalid_leakage"] or m["budget_violations"] or m["invalid_ledger_chains"]
                              for m in metrics.values()):
        raise SystemExit("Integrity gate failed; scientific superiority is a separate gate")


if __name__ == "__main__":
    main()
