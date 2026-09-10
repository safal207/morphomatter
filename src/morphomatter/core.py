"""Minimal transition-state simulator for MorphoMatter.

This module is intentionally dimensionless. Its parameters are algorithmic
proxies for controllable environmental conditions and MUST NOT be interpreted
as calibrated temperature, pressure, magnetic field, or material constants.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Iterable


class Phase(IntEnum):
    DISORDERED = 0
    METASTABLE = 1
    ORDERED = 2


@dataclass(frozen=True)
class ModelConfig:
    width: int = 8
    height: int = 8
    transition_threshold: float = 0.55
    metastable_threshold: float = 0.15
    neighbor_coupling: float = 0.45
    memory_decay: float = 0.0

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.transition_threshold <= 0 or self.metastable_threshold <= 0:
            raise ValueError("thresholds must be positive")
        if self.neighbor_coupling < 0:
            raise ValueError("neighbor_coupling must be non-negative")
        if not 0.0 <= self.memory_decay <= 1.0:
            raise ValueError("memory_decay must be in [0, 1]")


@dataclass(frozen=True)
class Conditions:
    """Dimensionless controls for one transition step.

    `drive` is the net external tendency toward order (+) or disorder (-).
    `coupling_scale` changes how strongly local neighbors influence a site.
    `threshold_scale` changes how hard it is to cross a phase boundary.
    """

    drive: float = 0.0
    coupling_scale: float = 1.0
    threshold_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.coupling_scale < 0:
            raise ValueError("coupling_scale must be non-negative")
        if self.threshold_scale <= 0:
            raise ValueError("threshold_scale must be positive")


@dataclass(frozen=True)
class Transition:
    tick: int
    site: int
    before: Phase
    after: Phase
    activation: float
    neighbor_order: float
    conditions: Conditions


class TransitionLattice:
    """Synchronous lattice whose state changes by crossing local thresholds."""

    def __init__(
        self,
        initial: Iterable[Phase | int],
        *,
        config: ModelConfig | None = None,
    ) -> None:
        self.config = config or ModelConfig()
        self.initial_state = tuple(Phase(int(value)) for value in initial)
        expected = self.config.width * self.config.height
        if len(self.initial_state) != expected:
            raise ValueError("initial state length must equal width * height")
        self.state = list(self.initial_state)
        self.activation = [0.0] * expected
        self.tick = 0
        self.trace: list[Transition] = []

    def _neighbors(self, site: int) -> tuple[int, ...]:
        row, col = divmod(site, self.config.width)
        result: list[int] = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = row + dr, col + dc
            if 0 <= rr < self.config.height and 0 <= cc < self.config.width:
                result.append(rr * self.config.width + cc)
        return tuple(result)

    @staticmethod
    def _order_value(phase: Phase) -> float:
        return float(phase) / float(Phase.ORDERED)

    def ordered_fraction(self) -> float:
        return sum(p is Phase.ORDERED for p in self.state) / len(self.state)

    def organization_score(self) -> float:
        """Mean normalized phase order in [0, 1]."""
        return sum(self._order_value(p) for p in self.state) / len(self.state)

    def step(self, conditions: Conditions) -> tuple[Transition, ...]:
        next_state = self.state.copy()
        next_activation = self.activation.copy()
        emitted: list[Transition] = []
        logical_tick = self.tick + 1

        for site, phase in enumerate(self.state):
            neighbors = self._neighbors(site)
            own = self._order_value(phase)
            neighbor_order = (
                sum(self._order_value(self.state[n]) for n in neighbors) / len(neighbors)
                if neighbors
                else own
            )
            coupling = self.config.neighbor_coupling * conditions.coupling_scale
            local_drive = conditions.drive + coupling * (neighbor_order - own)
            activation = self.config.memory_decay * self.activation[site] + local_drive
            threshold = (
                self.config.metastable_threshold
                if phase is Phase.METASTABLE
                else self.config.transition_threshold
            ) * conditions.threshold_scale

            direction = 1 if activation >= threshold else -1 if activation <= -threshold else 0
            candidate = max(int(Phase.DISORDERED), min(int(Phase.ORDERED), int(phase) + direction))
            after = Phase(candidate)
            if after is not phase:
                emitted.append(
                    Transition(
                        tick=logical_tick,
                        site=site,
                        before=phase,
                        after=after,
                        activation=activation,
                        neighbor_order=neighbor_order,
                        conditions=conditions,
                    )
                )
                next_state[site] = after
                activation = 0.0
            next_activation[site] = activation

        self.state = next_state
        self.activation = next_activation
        self.tick = logical_tick
        self.trace.extend(emitted)
        return tuple(emitted)

    def replay(self) -> tuple[Phase, ...]:
        state = list(self.initial_state)
        last_tick = 0
        for transition in self.trace:
            if transition.tick < last_tick:
                raise RuntimeError("trace is not monotone")
            last_tick = transition.tick
            if state[transition.site] is not transition.before:
                raise RuntimeError("trace does not compose")
            state[transition.site] = transition.after
        return tuple(state)


@dataclass
class PathGradientController:
    """Conventional baseline: strengthen conditions when progress stalls."""

    base_drive: float = 0.6
    boost: float = 0.25
    max_drive: float = 1.5
    _previous_score: float | None = None

    def choose(self, model: TransitionLattice) -> Conditions:
        score = model.organization_score()
        stalled = self._previous_score is not None and score <= self._previous_score
        drive = min(self.max_drive, self.base_drive + (self.boost if stalled else 0.0))
        self._previous_score = score
        return Conditions(drive=drive)
