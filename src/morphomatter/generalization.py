"""Statistical summaries for MorphoMatter Experiment 005.

All metrics here summarize simulation outcomes. Control effort is dimensionless
and must not be interpreted as physical energy.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from statistics import median
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EvaluationRun:
    success: bool
    effort_to_goal: float | None
    goal_tick: int | None
    replay_verified: bool


@dataclass(frozen=True)
class StrategySummary:
    runs: int
    successes: int
    success_rate: float
    success_ci95: tuple[float, float]
    median_effort: float | None
    effort_ci95: tuple[float, float] | None
    median_goal_tick: float | None
    goal_tick_ci95: tuple[float, float] | None
    replay_failures: int


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Two-sided Wilson score interval for a binomial proportion."""

    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must be in [0, total]")
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    margin = (
        z
        * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def percentile_bootstrap_interval(
    values: Sequence[float],
    *,
    seed: int,
    resamples: int = 2000,
) -> tuple[float, float]:
    """Deterministic percentile bootstrap interval for the sample median."""

    data = tuple(float(value) for value in values)
    if not data:
        raise ValueError("values must not be empty")
    if resamples <= 0:
        raise ValueError("resamples must be positive")
    rng = random.Random(seed)
    n = len(data)
    estimates = sorted(
        median(tuple(data[rng.randrange(n)] for _ in range(n)))
        for _ in range(resamples)
    )

    def percentile(q: float) -> float:
        if len(estimates) == 1:
            return estimates[0]
        position = q * (len(estimates) - 1)
        lower = int(math.floor(position))
        upper = int(math.ceil(position))
        if lower == upper:
            return estimates[lower]
        weight = position - lower
        return estimates[lower] * (1.0 - weight) + estimates[upper] * weight

    return percentile(0.025), percentile(0.975)


def summarize_runs(
    runs: Iterable[EvaluationRun],
    *,
    bootstrap_seed: int,
    resamples: int = 2000,
) -> StrategySummary:
    records = tuple(runs)
    if not records:
        raise ValueError("runs must not be empty")
    successes = tuple(run for run in records if run.success)
    efforts = tuple(
        float(run.effort_to_goal)
        for run in successes
        if run.effort_to_goal is not None
    )
    ticks = tuple(
        float(run.goal_tick)
        for run in successes
        if run.goal_tick is not None
    )
    if len(efforts) != len(successes) or len(ticks) != len(successes):
        raise ValueError("successful runs must contain effort and goal tick")
    success_ci = wilson_interval(len(successes), len(records))
    return StrategySummary(
        runs=len(records),
        successes=len(successes),
        success_rate=len(successes) / len(records),
        success_ci95=success_ci,
        median_effort=median(efforts) if efforts else None,
        effort_ci95=(
            percentile_bootstrap_interval(
                efforts, seed=bootstrap_seed, resamples=resamples
            )
            if efforts
            else None
        ),
        median_goal_tick=median(ticks) if ticks else None,
        goal_tick_ci95=(
            percentile_bootstrap_interval(
                ticks, seed=bootstrap_seed + 1, resamples=resamples
            )
            if ticks
            else None
        ),
        replay_failures=sum(not run.replay_verified for run in records),
    )


def paired_median_advantage_interval(
    learned: Sequence[EvaluationRun],
    cooperative: Sequence[EvaluationRun],
    *,
    seed: int = 5006,
    resamples: int = 2000,
) -> tuple[float, tuple[float, float], int]:
    """Median paired effort advantage cooperative - learned where both succeed."""

    if len(learned) != len(cooperative):
        raise ValueError("paired sequences must have equal length")
    differences: list[float] = []
    for left, right in zip(learned, cooperative):
        if not left.success or not right.success:
            continue
        if left.effort_to_goal is None or right.effort_to_goal is None:
            raise ValueError("successful paired runs require effort")
        differences.append(right.effort_to_goal - left.effort_to_goal)
    if not differences:
        raise ValueError("no jointly successful pairs")
    interval = percentile_bootstrap_interval(
        differences, seed=seed, resamples=resamples
    )
    return median(differences), interval, len(differences)
