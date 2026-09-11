"""Explore condition space and search transition schedules.

The explorer is deliberately dimensionless. It maps algorithmic control
conditions to model outcomes and must not be read as a calibrated physical
phase diagram.
"""
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import product
from typing import Iterable, Sequence

from .core import Conditions, ModelConfig, Phase, TransitionLattice


@dataclass(frozen=True)
class PhaseMapRecord:
    conditions: Conditions
    steps: int
    organization_score: float
    ordered_fraction: float
    dominant_phase: Phase
    transition_count: int
    final_state: tuple[Phase, ...]


@dataclass(frozen=True)
class ScheduleResult:
    schedule: tuple[Conditions, ...]
    cost: float
    organization_score: float
    final_state: tuple[Phase, ...]


def condition_grid(
    drives: Iterable[float],
    coupling_scales: Iterable[float] = (1.0,),
    threshold_scales: Iterable[float] = (1.0,),
) -> tuple[Conditions, ...]:
    """Return a deterministic Cartesian grid of dimensionless conditions."""

    return tuple(
        Conditions(
            drive=float(drive),
            coupling_scale=float(coupling),
            threshold_scale=float(threshold),
        )
        for drive, coupling, threshold in product(
            tuple(drives), tuple(coupling_scales), tuple(threshold_scales)
        )
    )


def _dominant_phase(state: Sequence[Phase]) -> Phase:
    counts = {phase: 0 for phase in Phase}
    for phase in state:
        counts[phase] += 1
    return max(Phase, key=lambda phase: (counts[phase], int(phase)))


def _action_cost(conditions: Conditions) -> float:
    """Simple declared control-effort baseline, not a physical energy model."""

    return (
        abs(conditions.drive)
        + 0.1 * abs(conditions.coupling_scale - 1.0)
        + 0.1 * abs(conditions.threshold_scale - 1.0)
    )


class TransitionMapExplorer:
    """Scan fixed conditions and search bounded schedules to a target score."""

    def __init__(self, config: ModelConfig, *, steps_per_point: int = 3) -> None:
        if steps_per_point <= 0:
            raise ValueError("steps_per_point must be positive")
        self.config = config
        self.steps_per_point = int(steps_per_point)

    def scan(
        self,
        initial: Iterable[Phase | int],
        conditions_space: Iterable[Conditions],
    ) -> tuple[PhaseMapRecord, ...]:
        initial_state = tuple(Phase(int(value)) for value in initial)
        records: list[PhaseMapRecord] = []
        for conditions in tuple(conditions_space):
            model = TransitionLattice(initial_state, config=self.config)
            for _ in range(self.steps_per_point):
                model.step(conditions)
            final_state = tuple(model.state)
            records.append(
                PhaseMapRecord(
                    conditions=conditions,
                    steps=self.steps_per_point,
                    organization_score=model.organization_score(),
                    ordered_fraction=model.ordered_fraction(),
                    dominant_phase=_dominant_phase(final_state),
                    transition_count=len(model.trace),
                    final_state=final_state,
                )
            )
        return tuple(records)

    def find_schedule(
        self,
        initial: Iterable[Phase | int],
        conditions_space: Iterable[Conditions],
        *,
        goal_score: float = 1.0,
        max_steps: int = 4,
    ) -> ScheduleResult | None:
        """Find a low-declared-cost schedule with a bounded Dijkstra search.

        v0 schedule search requires memory_decay == 0. With path memory enabled,
        phase state alone is insufficient to identify a search node and a future
        explorer must include hidden activation/history state explicitly.
        """

        if self.config.memory_decay != 0.0:
            raise ValueError("v0 schedule search requires memory_decay == 0")
        if not 0.0 <= goal_score <= 1.0:
            raise ValueError("goal_score must be in [0, 1]")
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")

        actions = tuple(conditions_space)
        initial_state = tuple(Phase(int(value)) for value in initial)
        initial_model = TransitionLattice(initial_state, config=self.config)
        if initial_model.organization_score() >= goal_score:
            return ScheduleResult((), 0.0, initial_model.organization_score(), initial_state)

        serial = 0
        queue: list[tuple[float, int, int, tuple[Phase, ...], tuple[Conditions, ...]]] = []
        heappush(queue, (0.0, 0, serial, initial_state, ()))
        best: dict[tuple[tuple[Phase, ...], int], float] = {(initial_state, 0): 0.0}

        while queue:
            cost, depth, _, state, schedule = heappop(queue)
            if cost > best.get((state, depth), float("inf")) + 1e-12:
                continue
            model = TransitionLattice(state, config=self.config)
            score = model.organization_score()
            if score >= goal_score:
                return ScheduleResult(schedule, cost, score, state)
            if depth >= max_steps:
                continue

            for conditions in actions:
                candidate = TransitionLattice(state, config=self.config)
                candidate.step(conditions)
                next_state = tuple(candidate.state)
                # With zero memory, a no-op step cannot unlock a later transition.
                if next_state == state:
                    continue
                next_depth = depth + 1
                next_cost = cost + _action_cost(conditions)
                key = (next_state, next_depth)
                if next_cost >= best.get(key, float("inf")) - 1e-12:
                    continue
                best[key] = next_cost
                serial += 1
                heappush(
                    queue,
                    (next_cost, next_depth, serial, next_state, schedule + (conditions,)),
                )

        return None
