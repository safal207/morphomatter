"""Damage/recovery helpers for MorphoMatter Experiment 003.

This module compares recovery strategies on the same damaged algorithmic state
and deterministic stochastic surface. Its control-effort score is dimensionless
and MUST NOT be interpreted as physical energy, power, or material efficiency.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping

from .core import Conditions, Phase
from .nucleation import NucleationConfig, NucleationLattice, NucleationTransition


@dataclass(frozen=True)
class DamageIntervention:
    sites: tuple[int, ...]
    before: tuple[Phase, ...]
    after: tuple[Phase, ...]
    ordered_sites_removed: int


@dataclass(frozen=True)
class RecoveryResult:
    name: str
    initial_ordered_fraction: float
    final_ordered_fraction: float
    first_goal_tick: int | None
    control_effort: float
    mechanism_counts: tuple[tuple[str, int], ...]
    trace: tuple[NucleationTransition, ...]
    final_state: tuple[Phase, ...]
    replay_verified: bool

    @property
    def gain(self) -> float:
        return self.final_ordered_fraction - self.initial_ordered_fraction

    @property
    def gain_per_effort(self) -> float:
        return self.gain / self.control_effort if self.control_effort > 0 else 0.0


def rectangular_sites(
    *,
    width: int,
    height: int,
    top: int,
    left: int,
    rows: int,
    cols: int,
) -> tuple[int, ...]:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    if top < 0 or left < 0 or top + rows > height or left + cols > width:
        raise ValueError("damage rectangle must fit inside lattice")
    return tuple(
        row * width + col
        for row in range(top, top + rows)
        for col in range(left, left + cols)
    )


def apply_damage(
    state: Iterable[Phase | int],
    sites: Iterable[int],
) -> DamageIntervention:
    before = tuple(Phase(int(value)) for value in state)
    selected = tuple(sorted(set(int(site) for site in sites)))
    if not selected:
        raise ValueError("at least one damage site is required")
    if selected[0] < 0 or selected[-1] >= len(before):
        raise IndexError("damage site outside state")

    after = list(before)
    ordered_sites_removed = 0
    for site in selected:
        if after[site] is Phase.ORDERED:
            ordered_sites_removed += 1
        after[site] = Phase.DISORDERED

    return DamageIntervention(
        sites=selected,
        before=before,
        after=tuple(after),
        ordered_sites_removed=ordered_sites_removed,
    )


def declared_control_effort(schedule: Iterable[Conditions]) -> float:
    """Declared algorithmic actuation score, deliberately not physical energy."""

    return sum(
        abs(conditions.drive)
        + 0.1 * abs(conditions.coupling_scale - 1.0)
        + 0.1 * abs(conditions.threshold_scale - 1.0)
        for conditions in schedule
    )


def run_recovery(
    name: str,
    initial: Iterable[Phase | int],
    *,
    config: NucleationConfig,
    schedule: Iterable[Conditions],
    goal_fraction: float = 0.90,
) -> RecoveryResult:
    if not 0.0 <= goal_fraction <= 1.0:
        raise ValueError("goal_fraction must be in [0, 1]")

    initial_state = tuple(Phase(int(value)) for value in initial)
    steps = tuple(schedule)
    model = NucleationLattice(initial_state, config=config)
    initial_fraction = model.ordered_fraction()
    first_goal_tick: int | None = 0 if initial_fraction >= goal_fraction else None

    for conditions in steps:
        model.step(conditions)
        if first_goal_tick is None and model.ordered_fraction() >= goal_fraction:
            first_goal_tick = model.tick

    counts = Counter(event.mechanism for event in model.trace)
    replay_verified = model.replay() == tuple(model.state)
    return RecoveryResult(
        name=name,
        initial_ordered_fraction=initial_fraction,
        final_ordered_fraction=model.ordered_fraction(),
        first_goal_tick=first_goal_tick,
        control_effort=declared_control_effort(steps),
        mechanism_counts=tuple(sorted(counts.items())),
        trace=tuple(model.trace),
        final_state=tuple(model.state),
        replay_verified=replay_verified,
    )


def compare_recovery_strategies(
    initial: Iterable[Phase | int],
    *,
    config: NucleationConfig,
    strategies: Mapping[str, Iterable[Conditions]],
    goal_fraction: float = 0.90,
) -> tuple[RecoveryResult, ...]:
    initial_state = tuple(Phase(int(value)) for value in initial)
    return tuple(
        run_recovery(
            name,
            initial_state,
            config=config,
            schedule=schedule,
            goal_fraction=goal_fraction,
        )
        for name, schedule in strategies.items()
    )
