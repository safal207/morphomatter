"""Finite-budget continuous model-predictive planner for Experiment 010.

The planner has exact access to the synthetic transition surrogate, current
state/tick, and material seed. This is intentionally stronger than the learned
policies and should be treated as a software reachability probe, not a physical
controller architecture.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from statistics import fmean, pstdev
from typing import Sequence

from .core import Conditions, Phase
from .nucleation import NucleationConfig, NucleationLattice
from .recovery import declared_control_effort


DRIVE_BOUNDS = (0.02, 0.80)
COUPLING_BOUNDS = (0.00, 1.80)
THRESHOLD_BOUNDS = (0.70, 0.90)
LOOKAHEAD = 3
SEARCH_ITERATIONS = 3
CANDIDATES_PER_ITERATION = 48
ELITE_COUNT = 8
STD_FLOOR_FRACTION = 0.10


@dataclass(frozen=True)
class CandidateEvaluation:
    schedule: tuple[Conditions, ...]
    reached_goal: bool
    goal_step: int | None
    final_ordered_fraction: float
    final_metastable_fraction: float
    effort: float

    @property
    def rank(self) -> tuple[int, int, float, float, float]:
        # Lexicographic ranking frozen by Experiment 010 preregistration.
        return (
            1 if self.reached_goal else 0,
            -(self.goal_step if self.goal_step is not None else 10_000),
            self.final_ordered_fraction,
            self.final_metastable_fraction,
            -self.effort,
        )


@dataclass(frozen=True)
class ContinuousMPCResult:
    schedule: tuple[Conditions, ...]
    final_ordered_fraction: float
    first_goal_tick: int | None
    control_effort: float
    replay_verified: bool


def validate_planner_protocol() -> None:
    if DRIVE_BOUNDS != (0.02, 0.80):
        raise RuntimeError("Experiment 010 drive bounds changed")
    if COUPLING_BOUNDS != (0.00, 1.80):
        raise RuntimeError("Experiment 010 coupling bounds changed")
    if THRESHOLD_BOUNDS != (0.70, 0.90):
        raise RuntimeError("Experiment 010 threshold bounds changed")
    if LOOKAHEAD != 3 or SEARCH_ITERATIONS != 3:
        raise RuntimeError("Experiment 010 horizon/iteration budget changed")
    if CANDIDATES_PER_ITERATION != 48 or ELITE_COUNT != 8:
        raise RuntimeError("Experiment 010 candidate/elite budget changed")
    if STD_FLOOR_FRACTION != 0.10:
        raise RuntimeError("Experiment 010 standard-deviation floor changed")


def _clip(value: float, bounds: tuple[float, float]) -> float:
    return max(bounds[0], min(bounds[1], float(value)))


def _forecast_from(model: NucleationLattice) -> NucleationLattice:
    """Create a Markov forecast clone at the same state and logical tick."""

    forecast = NucleationLattice(tuple(model.state), config=model.config)
    forecast.tick = model.tick
    return forecast


def _evaluate_candidate(
    model: NucleationLattice,
    schedule: Sequence[Conditions],
    *,
    goal_fraction: float,
) -> CandidateEvaluation:
    forecast = _forecast_from(model)
    reached_goal = forecast.ordered_fraction() >= goal_fraction
    goal_step: int | None = 0 if reached_goal else None
    used: list[Conditions] = []

    for relative_step, conditions in enumerate(schedule, start=1):
        if reached_goal:
            break
        used.append(conditions)
        forecast.step(conditions)
        if forecast.ordered_fraction() >= goal_fraction:
            reached_goal = True
            goal_step = relative_step

    return CandidateEvaluation(
        schedule=tuple(schedule),
        reached_goal=reached_goal,
        goal_step=goal_step,
        final_ordered_fraction=forecast.ordered_fraction(),
        final_metastable_fraction=forecast.metastable_fraction(),
        effort=declared_control_effort(used),
    )


def _uniform_schedule(rng: random.Random, horizon: int) -> tuple[Conditions, ...]:
    return tuple(
        Conditions(
            drive=rng.uniform(*DRIVE_BOUNDS),
            coupling_scale=rng.uniform(*COUPLING_BOUNDS),
            threshold_scale=rng.uniform(*THRESHOLD_BOUNDS),
        )
        for _ in range(horizon)
    )


def _elite_distribution(
    elites: Sequence[CandidateEvaluation],
    horizon: int,
) -> tuple[tuple[tuple[float, float], ...], ...]:
    """Return per-step ((mean,std) x 3) distribution fitted to elites."""

    ranges = (
        DRIVE_BOUNDS[1] - DRIVE_BOUNDS[0],
        COUPLING_BOUNDS[1] - COUPLING_BOUNDS[0],
        THRESHOLD_BOUNDS[1] - THRESHOLD_BOUNDS[0],
    )
    result: list[tuple[tuple[float, float], ...]] = []
    for step in range(horizon):
        columns = (
            [candidate.schedule[step].drive for candidate in elites],
            [candidate.schedule[step].coupling_scale for candidate in elites],
            [candidate.schedule[step].threshold_scale for candidate in elites],
        )
        step_params: list[tuple[float, float]] = []
        for values, full_range in zip(columns, ranges):
            mean = fmean(values)
            sigma = pstdev(values) if len(values) > 1 else 0.0
            sigma = max(sigma, STD_FLOOR_FRACTION * full_range)
            step_params.append((mean, sigma))
        result.append(tuple(step_params))
    return tuple(result)


def _gaussian_schedule(
    rng: random.Random,
    distribution: tuple[tuple[tuple[float, float], ...], ...],
) -> tuple[Conditions, ...]:
    bounds = (DRIVE_BOUNDS, COUPLING_BOUNDS, THRESHOLD_BOUNDS)
    schedule: list[Conditions] = []
    for step_params in distribution:
        values = [
            _clip(rng.gauss(mean, sigma), component_bounds)
            for (mean, sigma), component_bounds in zip(step_params, bounds)
        ]
        schedule.append(
            Conditions(
                drive=values[0],
                coupling_scale=values[1],
                threshold_scale=values[2],
            )
        )
    return tuple(schedule)


def plan_next_conditions(
    model: NucleationLattice,
    *,
    remaining_ticks: int,
    goal_fraction: float,
    planner_seed: int,
) -> tuple[Conditions, CandidateEvaluation]:
    """Run the frozen finite-budget CEM search and return one receding action."""

    validate_planner_protocol()
    if remaining_ticks <= 0:
        raise ValueError("remaining_ticks must be positive")
    if not 0.0 <= goal_fraction <= 1.0:
        raise ValueError("goal_fraction must be in [0, 1]")

    horizon = min(LOOKAHEAD, int(remaining_ticks))
    rng = random.Random(int(planner_seed))
    distribution = None
    best: CandidateEvaluation | None = None

    for iteration in range(SEARCH_ITERATIONS):
        candidates: list[CandidateEvaluation] = []
        for _ in range(CANDIDATES_PER_ITERATION):
            if iteration == 0:
                schedule = _uniform_schedule(rng, horizon)
            else:
                assert distribution is not None
                schedule = _gaussian_schedule(rng, distribution)
            candidates.append(
                _evaluate_candidate(
                    model,
                    schedule,
                    goal_fraction=goal_fraction,
                )
            )

        candidates.sort(key=lambda candidate: candidate.rank, reverse=True)
        elites = tuple(candidates[:ELITE_COUNT])
        best = elites[0]
        distribution = _elite_distribution(elites, horizon)

    assert best is not None
    return best.schedule[0], best


def run_continuous_mpc(
    initial: Sequence[Phase | int],
    *,
    config: NucleationConfig,
    lambda_index: int,
    case_index: int,
    max_steps: int = 9,
    goal_fraction: float = 0.90,
) -> ContinuousMPCResult:
    """Execute the preregistered receding-horizon continuous planner."""

    validate_planner_protocol()
    if max_steps != 9:
        raise ValueError("Experiment 010 execution horizon must remain 9")
    if goal_fraction != 0.90:
        raise ValueError("Experiment 010 goal must remain 0.90")

    model = NucleationLattice(initial, config=config)
    schedule: list[Conditions] = []
    first_goal_tick: int | None = 0 if model.ordered_fraction() >= goal_fraction else None

    while model.tick < max_steps and first_goal_tick is None:
        planner_seed = (
            1_010_000
            + int(lambda_index) * 100_000
            + int(case_index) * 1_000
            + model.tick
        )
        conditions, _best = plan_next_conditions(
            model,
            remaining_ticks=max_steps - model.tick,
            goal_fraction=goal_fraction,
            planner_seed=planner_seed,
        )
        schedule.append(conditions)
        model.step(conditions)
        if model.ordered_fraction() >= goal_fraction:
            first_goal_tick = model.tick

    replay = model.replay() == tuple(model.state)
    return ContinuousMPCResult(
        schedule=tuple(schedule),
        final_ordered_fraction=model.ordered_fraction(),
        first_goal_tick=first_goal_tick,
        control_effort=declared_control_effort(schedule),
        replay_verified=replay,
    )
