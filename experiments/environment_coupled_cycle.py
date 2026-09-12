"""Run the prospective Exp021 protocol without treating negative results as errors.

The dynamics/protocol are inherited unchanged from commit 3550d8c4. This runner
checks integrity before any primary trajectory and saves all stage snapshots.
No learned AI policy or physical material calibration is involved.
"""
from __future__ import annotations

import csv
from dataclasses import asdict
from hashlib import sha256
import json
from math import isclose, isfinite, log10
from pathlib import Path
import random
from statistics import mean, median
import subprocess
import sys
import unittest

from morphomatter import environment_cycle as cycle
from morphomatter.particle_anisotropy import PARTICLE_BY_NAME
from morphomatter.translational_assembly import GRID_SIZE, PARTICLE_COUNT, spatial_metrics

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SAMPLES = 2000
BOOTSTRAP_SEEDS = (21101, 21102)


def describe(values):
    values = tuple(float(v) for v in values)
    if not values or not all(isfinite(v) for v in values):
        raise ValueError("finite, nonempty measurements required")
    return {"n": len(values), "mean": mean(values), "median": median(values),
            "minimum": min(values), "maximum": max(values)}


def percentile(ordered, probability):
    """Linear interpolation at (n-1)*p; no distributional assumption."""
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (position - lower) * (ordered[upper] - ordered[lower])


def bootstrap_mean_interval(values, seed):
    values = tuple(values)
    rng = random.Random(seed)
    estimates = sorted(mean(values[rng.randrange(len(values))] for _ in values)
                       for _ in range(BOOTSTRAP_SAMPLES))
    return [percentile(estimates, 0.025), percentile(estimates, 0.975)]


def endpoints(result):
    first = result.stages[0].metrics.binding_utilization
    high = result.stages[len(cycle.I_UP) - 1].metrics.binding_utilization
    relaxed = result.relaxed.metrics.binding_utilization
    return {"first_utilization": first, "high_utilization": high,
            "relaxed_utilization": relaxed, "assembly_gain": high - first,
            "release_drop": high - relaxed, "return_error": abs(relaxed - first)}


def trace_integrity_failures(result):
    topology = PARTICLE_BY_NAME[cycle.TOPOLOGY_NAME]
    failures = 0
    last_accepted = 0
    snapshots = result.stages + (result.relaxed,)
    for index, snapshot in enumerate(snapshots):
        state = snapshot.state
        failures += int(len(state.positions) != PARTICLE_COUNT or len(set(state.positions)) != PARTICLE_COUNT)
        failures += int(not all(0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE for x, y in state.positions))
        failures += int(not all(value in (0, 1, 2, 3) for value in state.orientations))
        coefficients = cycle.energy_coefficients(snapshot.external_strength, coupled=result.coupled)
        measured = cycle.contact_energy(topology, state, coefficients)
        failures += int(not isfinite(snapshot.energy) or not isclose(snapshot.energy, measured, abs_tol=1e-12))
        failures += int(snapshot.contacts != len(cycle.occupied_contacts(state)))
        failures += int(snapshot.metrics != spatial_metrics(topology, state))
        failures += int(not all(isfinite(v) for v in asdict(snapshot.metrics).values()))
        failures += int(not 0 <= snapshot.metrics.binding_utilization <= 1)
        if index < len(result.stages):
            expected = (cycle.WARMUP_SWEEPS + (index + 1) * result.stage_sweeps) * PARTICLE_COUNT
        else:
            expected = (cycle.WARMUP_SWEEPS + len(result.stages) * result.stage_sweeps
                        + cycle.RELAXATION_SWEEPS) * PARTICLE_COUNT
        failures += int(snapshot.proposals != expected)
        failures += int(not last_accepted <= snapshot.accepted <= snapshot.proposals)
        last_accepted = snapshot.accepted
    return failures


def path_separation(results):
    rows = []
    for index, strength in enumerate(cycle.I_UP):
        outward = mean(r.stages[index].metrics.binding_utilization for r in results)
        returning = mean(r.stages[len(cycle.I_CYCLE) - 1 - index].metrics.binding_utilization for r in results)
        rows.append({"I": strength, "outward_mean": outward, "return_mean": returning,
                     "signed_return_minus_outward": returning - outward})
    area = 0.0
    for left, right in zip(rows, rows[1:]):
        width = log10(right["I"]) - log10(left["I"])
        area += width * (abs(left["signed_return_minus_outward"])
                         + abs(right["signed_return_minus_outward"])) / 2.0
    area /= log10(cycle.I_UP[-1]) - log10(cycle.I_UP[0])
    return {"points": rows, "normalized_absolute_area": area,
            "descriptive_flag_ge_0_05": area >= 0.05}


def provenance():
    paths = sorted((ROOT / "src" / "morphomatter").glob("*.py"))
    paths += [ROOT / "tests" / "test_environment_cycle.py", Path(__file__).resolve(),
              ROOT / "docs" / "EXPERIMENT_021_PREREGISTRATION.md"]
    hashes = {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths}
    try:
        checkout = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        checkout = None
    return {"checkout_sha": checkout,
            "inherited_adapter_commit": "3550d8c4c7ff32f1639ce536cd83dccef802b067",
            "preregistration_commit": "af50186071ff320fe2b799e031359ddeb90bf29a",
            "python_version": sys.version, "source_sha256": hashes}


def write_evidence(summary, primary, controls):
    directory = ROOT / "artifacts"
    directory.mkdir(exist_ok=True)
    traces = {"primary": [asdict(result) for result in primary],
              "counterfactual": [{"varying_labels": asdict(pair[0]),
                                    "constant_labels": asdict(pair[1])} for pair in controls]}
    raw = json.dumps(traces, sort_keys=True, separators=(",", ":"), allow_nan=False)
    summary["mechanical_evidence_sha256"] = sha256(raw.encode("utf-8")).hexdigest()
    (directory / "experiment_021_traces.json").write_text(raw + "\n", encoding="utf-8")
    (directory / "experiment_021_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    with (directory / "experiment_021_stages.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("seed", "sweeps_per_stage", "stage", "I",
                               "energy", "contacts", "utilization", "largest_component", "proposals", "accepted"))
        writer.writeheader()
        for result in primary:
            for index, snapshot in enumerate(result.stages + (result.relaxed,)):
                writer.writerow({"seed": result.seed, "sweeps_per_stage": result.stage_sweeps,
                                 "stage": index if index < len(result.stages) else "relaxed",
                                 "I": snapshot.external_strength, "energy": snapshot.energy,
                                 "contacts": snapshot.contacts, "utilization": snapshot.metrics.binding_utilization,
                                 "largest_component": snapshot.metrics.largest_component_fraction,
                                 "proposals": snapshot.proposals, "accepted": snapshot.accepted})


def main():
    cycle.validate_protocol()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_environment_cycle.py")
    validation = unittest.TextTestRunner(verbosity=2).run(suite)
    if validation.testsRun < 18 or not validation.wasSuccessful():
        raise SystemExit("Exp021 integrity tests failed or were not fully discovered; no primary experiment run")

    primary = []
    controls = []
    replay_failures = 0
    control_failures = 0
    invariant_failures = 0
    rate_summaries = {}
    for sweeps in cycle.SWEEP_RATES:
        group = []
        for seed in cycle.SEEDS:
            result = cycle.run_cycle(seed, sweeps)
            repeated = cycle.run_cycle(seed, sweeps)
            replay_failures += int(result != repeated)
            invariant_failures += trace_integrity_failures(result)
            invariant_failures += trace_integrity_failures(repeated)
            group.append(result)
            primary.append(result)
            print("TRAJECTORY", json.dumps({"seed": seed, "sweeps": sweeps, **endpoints(result)}, sort_keys=True), flush=True)
        values = [endpoints(result) for result in group]
        rate_summaries[str(sweeps)] = {
            "endpoints": {name: describe([row[name] for row in values]) for name in values[0]},
            "path_separation": path_separation(group),
        }

    for seed in cycle.CONTROL_SEEDS:
        varied = cycle.run_cycle(seed, 256, coupled=False)
        constant = cycle.run_cycle(seed, 256, coupled=False, schedule=(1.0,) * len(cycle.I_CYCLE))
        control_failures += int(varied.mechanical_trace() != constant.mechanical_trace())
        invariant_failures += trace_integrity_failures(varied) + trace_integrity_failures(constant)
        controls.append((varied, constant))

    slow = [endpoints(result) for result in primary if result.stage_sweeps == 256]
    gains = [item["assembly_gain"] for item in slow]
    drops = [item["release_drop"] for item in slow]
    checks = {
        "assembly_gain_median_ge_0_25": median(gains) >= 0.25,
        "release_drop_median_ge_0_25": median(drops) >= 0.25,
        "return_error_median_le_0_125": median(item["return_error"] for item in slow) <= 0.125,
        "relaxed_utilization_median_le_0_125": median(item["relaxed_utilization"] for item in slow) <= 0.125,
        "replay_exact": replay_failures == 0,
        "counterfactual_labels_invariant": control_failures == 0,
        "integrity_tests_passed": validation.wasSuccessful(),
        "trace_invariants_passed": invariant_failures == 0,
    }
    integrity_ok = replay_failures == 0 and control_failures == 0 and invariant_failures == 0
    if not integrity_ok:
        label = "INVALID_EXPERIMENT_INTEGRITY_FAILURE"
    else:
        label = ("ENVIRONMENT_COUPLED_ASSEMBLY_AND_RELEASE" if all(checks.values())
                 else "ENVIRONMENT_CYCLE_MIXED_OR_NEGATIVE")
    summary = {
        "experiment": "021", "label": label, "provenance": provenance(),
        "integrity_tests_run": validation.testsRun, "primary_trajectories": len(primary),
        "repeat_trajectories": len(primary), "counterfactual_pairs": len(controls),
        "replay_failures": replay_failures, "counterfactual_control_failures": control_failures,
        "trace_invariant_failures": invariant_failures, "criteria": checks, "rates": rate_summaries,
        "assembly_gain_mean_ci95": bootstrap_mean_interval(gains, BOOTSTRAP_SEEDS[0]),
        "release_drop_mean_ci95": bootstrap_mean_interval(drops, BOOTSTRAP_SEEDS[1]),
        "bootstrap": {"samples": BOOTSTRAP_SAMPLES, "seeds": BOOTSTRAP_SEEDS,
                      "unit": "paired seed-level endpoints for one finite synthetic model"},
        "fixed_energy_control_gain": describe([endpoints(pair[0])["assembly_gain"] for pair in controls]),
        "nonclaims": "Contact-only finite lattice Monte Carlo; no calibrated chemistry, equilibrium hysteresis, learned AI, or real programmable matter.",
    }
    write_evidence(summary, primary, controls)
    compact = {key: value for key, value in summary.items() if key != "provenance"}
    print("SUMMARY_JSON=" + json.dumps(compact, sort_keys=True, allow_nan=False), flush=True)
    print("CHECKOUT_SHA=" + str(summary["provenance"]["checkout_sha"]), flush=True)
    print("PREREGISTERED_RESULT=" + label, flush=True)
    if not integrity_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
