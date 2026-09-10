"""Seeded nucleation/frontier toy model for MorphoMatter Experiment 002.

This module is an algorithmic research model, not a calibrated model of water,
crystallization, magnetic colloids, or any physical material. Probabilities are
dimensionless and only provide a reproducible sandbox for studying the idea
that global conditions can create local nuclei and then let local coupling
propagate order through a moving frontier.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable

from .core import Conditions, Phase


def _clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _deterministic_unit(seed: int, tick: int, site: int, mechanism: str) -> float:
    """Stable pseudo-random draw in [0, 1) for exact replay/comparison.

    The draw is keyed by seed/tick/site/mechanism so different condition
    schedules can be compared under the same deterministic stochastic surface.
    """

    digest = hashlib.sha256(
        f"{seed}|{tick}|{site}|{mechanism}".encode("ascii")
    ).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


@dataclass(frozen=True)
class NucleationConfig:
    width: int = 9
    height: int = 9
    seed: int = 26
    spontaneous_rate: float = 0.02
    nucleation_drive_gain: float = 0.18
    frontier_base: float = 0.08
    frontier_neighbor_gain: float = 0.75
    frontier_drive_gain: float = 0.18
    commit_base: float = 0.25
    commit_neighbor_gain: float = 0.35
    commit_drive_gain: float = 0.35
    barrier: float = 0.10

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        for value in (
            self.spontaneous_rate,
            self.nucleation_drive_gain,
            self.frontier_base,
            self.frontier_neighbor_gain,
            self.frontier_drive_gain,
            self.commit_base,
            self.commit_neighbor_gain,
            self.commit_drive_gain,
            self.barrier,
        ):
            if value < 0:
                raise ValueError("rates, gains, and barrier must be non-negative")


@dataclass(frozen=True)
class NucleationTransition:
    tick: int
    site: int
    before: Phase
    after: Phase
    mechanism: str
    probability: float
    random_draw: float
    ordered_neighbor_fraction: float
    conditions: Conditions


class NucleationLattice:
    """One-way DISORDERED → METASTABLE → ORDERED nucleation/frontier model."""

    def __init__(
        self,
        initial: Iterable[Phase | int] | None = None,
        *,
        config: NucleationConfig | None = None,
    ) -> None:
        self.config = config or NucleationConfig()
        cells = self.config.width * self.config.height
        if initial is None:
            initial_state = (Phase.DISORDERED,) * cells
        else:
            initial_state = tuple(Phase(int(value)) for value in initial)
        if len(initial_state) != cells:
            raise ValueError("initial state length must equal width * height")

        self.initial_state = initial_state
        self.state = list(initial_state)
        self.tick = 0
        self.trace: list[NucleationTransition] = []

    def _neighbors(self, site: int) -> tuple[int, ...]:
        row, col = divmod(site, self.config.width)
        result: list[int] = []
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = row + dr, col + dc
            if 0 <= rr < self.config.height and 0 <= cc < self.config.width:
                result.append(rr * self.config.width + cc)
        return tuple(result)

    def _ordered_neighbor_fraction(self, site: int) -> float:
        neighbors = self._neighbors(site)
        if not neighbors:
            return 0.0
        return sum(self.state[n] is Phase.ORDERED for n in neighbors) / len(neighbors)

    def ordered_fraction(self) -> float:
        return sum(phase is Phase.ORDERED for phase in self.state) / len(self.state)

    def metastable_fraction(self) -> float:
        return sum(phase is Phase.METASTABLE for phase in self.state) / len(self.state)

    def frontier_sites(self) -> tuple[int, ...]:
        """Non-ordered sites directly adjacent to at least one ordered site."""

        return tuple(
            site
            for site, phase in enumerate(self.state)
            if phase is not Phase.ORDERED
            and any(self.state[n] is Phase.ORDERED for n in self._neighbors(site))
        )

    def _transition_probability(
        self,
        phase: Phase,
        ordered_neighbor_fraction: float,
        conditions: Conditions,
    ) -> tuple[str, float] | None:
        cfg = self.config
        drive = max(0.0, conditions.drive)
        barrier = cfg.barrier * conditions.threshold_scale

        if phase is Phase.DISORDERED:
            if ordered_neighbor_fraction <= 0.0:
                probability = (
                    cfg.spontaneous_rate
                    + cfg.nucleation_drive_gain * drive
                    - barrier
                )
                return "nucleation", _clamp_probability(probability)

            probability = (
                cfg.frontier_base
                + cfg.frontier_neighbor_gain
                * ordered_neighbor_fraction
                * conditions.coupling_scale
                + cfg.frontier_drive_gain * drive
                - barrier
            )
            return "frontier_growth", _clamp_probability(probability)

        if phase is Phase.METASTABLE:
            probability = (
                cfg.commit_base
                + cfg.commit_neighbor_gain
                * ordered_neighbor_fraction
                * conditions.coupling_scale
                + cfg.commit_drive_gain * drive
                - barrier
            )
            return "commit", _clamp_probability(probability)

        return None

    def step(self, conditions: Conditions) -> tuple[NucleationTransition, ...]:
        logical_tick = self.tick + 1
        next_state = self.state.copy()
        emitted: list[NucleationTransition] = []

        for site, phase in enumerate(self.state):
            candidate = self._transition_probability(
                phase, self._ordered_neighbor_fraction(site), conditions
            )
            if candidate is None:
                continue

            mechanism, probability = candidate
            draw = _deterministic_unit(
                self.config.seed, logical_tick, site, mechanism
            )
            if draw >= probability:
                continue

            after = (
                Phase.METASTABLE
                if phase is Phase.DISORDERED
                else Phase.ORDERED
            )
            event = NucleationTransition(
                tick=logical_tick,
                site=site,
                before=phase,
                after=after,
                mechanism=mechanism,
                probability=probability,
                random_draw=draw,
                ordered_neighbor_fraction=self._ordered_neighbor_fraction(site),
                conditions=conditions,
            )
            emitted.append(event)
            next_state[site] = after

        self.state = next_state
        self.tick = logical_tick
        self.trace.extend(emitted)
        return tuple(emitted)

    def run(self, schedule: Iterable[Conditions]) -> None:
        for conditions in schedule:
            self.step(conditions)

    def replay(self) -> tuple[Phase, ...]:
        state = list(self.initial_state)
        previous_tick = 0
        for event in self.trace:
            if event.tick < previous_tick:
                raise RuntimeError("transition trace is not monotone")
            previous_tick = event.tick
            if state[event.site] is not event.before:
                raise RuntimeError("transition trace does not compose")
            state[event.site] = event.after
        return tuple(state)

    def rows(self) -> tuple[str, ...]:
        glyph = {
            Phase.DISORDERED: ".",
            Phase.METASTABLE: "o",
            Phase.ORDERED: "#",
        }
        width = self.config.width
        return tuple(
            "".join(glyph[phase] for phase in self.state[start : start + width])
            for start in range(0, len(self.state), width)
        )
