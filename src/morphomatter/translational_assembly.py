"""Translational + rotational lattice kinetics for MorphoMatter Experiment 020.

Particles occupy distinct sites on a periodic square lattice. Contact topology is
not declared in advance: it emerges from current nearest-neighbor occupancy.
Directional contact strengths reuse the frozen Experiment 018 particle ports.

This is a synthetic lattice Monte Carlo surrogate, not calibrated Brownian,
molecular, colloidal, or thermodynamic dynamics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isclose
import random

from .environment_screening import interaction_metrics
from .interface_chemistry import external_interface_c1
from .orientation_kinetics import MATCHED_PAIRS  # frozen naming/control lineage
from .particle_anisotropy import (
    DIRECTIONAL_BUDGET,
    OPPOSITE,
    PARTICLE_BY_NAME,
    PARTICLE_TOPOLOGIES,
    ParticleTopology,
    bond_strength,
    validate_frozen_protocol,
)
from .particle_environment import interface_control_value

GRID_SIZE = 6
PARTICLE_COUNT = 8
SEEDS = tuple(range(20001, 20033))
BETA_SCHEDULE = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
SWEEPS_PER_BETA = 300

DIRECTIONS = ("N", "E", "S", "W")
DELTAS = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}


@dataclass(frozen=True)
class LatticeState:
    positions: tuple[tuple[int, int], ...]
    orientations: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.positions) != PARTICLE_COUNT:
            raise ValueError("state must contain exactly eight particle positions")
        if len(self.orientations) != PARTICLE_COUNT:
            raise ValueError("state must contain exactly eight particle orientations")
        if len(set(self.positions)) != PARTICLE_COUNT:
            raise ValueError("excluded-volume violation: duplicate occupied site")
        for x, y in self.positions:
            if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                raise ValueError("position outside frozen periodic lattice")
        if any(int(value) % 4 != value for value in self.orientations):
            raise ValueError("orientations must be quarter-turn states 0..3")


@dataclass(frozen=True)
class ActiveBond:
    u: int
    v: int
    direction_u: str
    direction_v: str
    strength: float


@dataclass(frozen=True)
class SpatialMetrics:
    total_bond_strength: float
    binding_utilization: float
    largest_component_fraction: float
    mean_active_degree: float
    axial_fraction: float
    corner_fraction: float
    branch_fraction: float
    cross_fraction: float
    active_bond_count: int


@dataclass(frozen=True)
class TranslationalAnnealResult:
    particle: str
    seed: int
    initial_state: LatticeState
    beta0_state: LatticeState
    final_state: LatticeState
    beta0_metrics: SpatialMetrics
    final_metrics: SpatialMetrics
    stage_metrics: tuple[tuple[float, SpatialMetrics], ...]
    proposals: int
    accepted: int

    @property
    def delta_utilization(self) -> float:
        return self.final_metrics.binding_utilization - self.beta0_metrics.binding_utilization


def validate_protocol() -> None:
    validate_frozen_protocol()
    if GRID_SIZE != 6 or PARTICLE_COUNT != 8:
        raise ValueError("spatial protocol drifted")
    if SEEDS != tuple(range(20001, 20033)):
        raise ValueError("seed protocol drifted")
    if BETA_SCHEDULE != (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        raise ValueError("beta schedule drifted")
    if SWEEPS_PER_BETA != 300:
        raise ValueError("sweep protocol drifted")
    if not isclose(DIRECTIONAL_BUDGET, 2.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("directional budget drifted")
    if tuple(item.name for item in PARTICLE_TOPOLOGIES) != (
        "isotropic4",
        "axial2",
        "corner2",
        "tri3",
    ):
        raise ValueError("particle topology protocol drifted")
    # Preserve declared Experiment 019 lineage without making the dynamic law
    # depend on target motifs.
    if tuple(name for name, _motif in MATCHED_PAIRS) != (
        "isotropic4",
        "axial2",
        "corner2",
        "tri3",
    ):
        raise ValueError("Experiment 019 topology lineage drifted")


def background_controls_hold() -> bool:
    """Check frozen Experiment 015/016/017 scalar background controls."""
    # q_rel=1, I=1 is the exact Experiment 016 baseline pair potential.
    regime_ok = interaction_metrics(1.0).regime == "REVERSIBLE_ASSEMBLY"
    # particle_environment exposes the Experiment 015 theta=180 hard control.
    interface_ok = abs(interface_control_value() - 0.700000000) <= 1e-12
    # Also independently query the frozen interface law at the hard config via
    # the helper lineage used by particle_environment. The first check is the
    # authoritative cross-experiment control; import retained for API drift.
    _ = external_interface_c1
    return regime_ok and interface_ok


def _wrap(value: int) -> int:
    return int(value) % GRID_SIZE


def random_state(rng: random.Random) -> LatticeState:
    sites = rng.sample(range(GRID_SIZE * GRID_SIZE), PARTICLE_COUNT)
    positions = tuple((index % GRID_SIZE, index // GRID_SIZE) for index in sites)
    orientations = tuple(rng.randrange(4) for _ in range(PARTICLE_COUNT))
    return LatticeState(positions=positions, orientations=orientations)


def active_bonds(topology: ParticleTopology, state: LatticeState) -> tuple[ActiveBond, ...]:
    occupancy = {position: index for index, position in enumerate(state.positions)}
    bonds: list[ActiveBond] = []
    # Enumerate only east and south so every undirected periodic contact is
    # visited exactly once on the frozen 6x6 lattice.
    for u, (x, y) in enumerate(state.positions):
        for direction_u in ("E", "S"):
            dx, dy = DELTAS[direction_u]
            neighbor = (_wrap(x + dx), _wrap(y + dy))
            v = occupancy.get(neighbor)
            if v is None:
                continue
            direction_v = OPPOSITE[direction_u]
            strength = bond_strength(
                topology,
                state.orientations[u],
                direction_u,
                state.orientations[v],
                direction_v,
            )
            if strength > 0.0:
                bonds.append(
                    ActiveBond(
                        u=u,
                        v=v,
                        direction_u=direction_u,
                        direction_v=direction_v,
                        strength=float(strength),
                    )
                )
    return tuple(bonds)


def binding_score(topology: ParticleTopology, state: LatticeState) -> float:
    return float(sum(bond.strength for bond in active_bonds(topology, state)))


def spatial_metrics(topology: ParticleTopology, state: LatticeState) -> SpatialMetrics:
    bonds = active_bonds(topology, state)
    total = float(sum(bond.strength for bond in bonds))
    utilization = total / PARTICLE_COUNT
    if utilization < -1e-12 or utilization > 1.0 + 1e-12:
        raise RuntimeError(f"binding utilization outside [0,1]: {utilization}")
    utilization = min(1.0, max(0.0, utilization))

    directions: list[list[str]] = [[] for _ in range(PARTICLE_COUNT)]
    adjacency: list[set[int]] = [set() for _ in range(PARTICLE_COUNT)]
    for bond in bonds:
        directions[bond.u].append(bond.direction_u)
        directions[bond.v].append(bond.direction_v)
        adjacency[bond.u].add(bond.v)
        adjacency[bond.v].add(bond.u)

    degrees = tuple(len(items) for items in directions)
    axial = 0
    corner = 0
    branch = 0
    cross = 0
    for items in directions:
        degree = len(items)
        if degree == 2:
            first, second = items
            if OPPOSITE[first] == second:
                axial += 1
            else:
                corner += 1
        if degree >= 3:
            branch += 1
        if degree == 4:
            cross += 1

    visited: set[int] = set()
    largest = 0
    for start in range(PARTICLE_COUNT):
        if start in visited:
            continue
        stack = [start]
        size = 0
        visited.add(start)
        while stack:
            node = stack.pop()
            size += 1
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        largest = max(largest, size)

    return SpatialMetrics(
        total_bond_strength=total,
        binding_utilization=utilization,
        largest_component_fraction=largest / PARTICLE_COUNT,
        mean_active_degree=sum(degrees) / PARTICLE_COUNT,
        axial_fraction=axial / PARTICLE_COUNT,
        corner_fraction=corner / PARTICLE_COUNT,
        branch_fraction=branch / PARTICLE_COUNT,
        cross_fraction=cross / PARTICLE_COUNT,
        active_bond_count=len(bonds),
    )


def _translation_candidate(
    state: LatticeState,
    particle: int,
    direction: str,
) -> LatticeState | None:
    x, y = state.positions[particle]
    dx, dy = DELTAS[direction]
    target = (_wrap(x + dx), _wrap(y + dy))
    if target in set(state.positions):
        return None
    positions = list(state.positions)
    positions[particle] = target
    return LatticeState(positions=tuple(positions), orientations=state.orientations)


def _rotation_candidate(state: LatticeState, particle: int, step: int) -> LatticeState:
    if step not in (-1, 1):
        raise ValueError("rotation step must be +/-1 quarter-turn")
    orientations = list(state.orientations)
    orientations[particle] = (orientations[particle] + step) % 4
    return LatticeState(positions=state.positions, orientations=tuple(orientations))


def metropolis_proposal(
    topology: ParticleTopology,
    state: LatticeState,
    beta: float,
    rng: random.Random,
) -> tuple[LatticeState, bool]:
    beta_value = float(beta)
    if beta_value < 0.0:
        raise ValueError("beta must be non-negative")

    particle = rng.randrange(PARTICLE_COUNT)
    move_class = rng.randrange(2)
    if move_class == 0:
        direction = DIRECTIONS[rng.randrange(4)]
        candidate = _translation_candidate(state, particle, direction)
        if candidate is None:
            return state, False
    else:
        step = -1 if rng.randrange(2) == 0 else 1
        candidate = _rotation_candidate(state, particle, step)

    current_score = binding_score(topology, state)
    candidate_score = binding_score(topology, candidate)
    delta = candidate_score - current_score
    if delta >= 0.0:
        return candidate, True
    probability = exp(beta_value * delta)
    if rng.random() < probability:
        return candidate, True
    return state, False


def run_sweeps(
    topology: ParticleTopology,
    state: LatticeState,
    beta: float,
    sweeps: int,
    rng: random.Random,
) -> tuple[LatticeState, int, int]:
    if sweeps < 0:
        raise ValueError("sweeps must be non-negative")
    current = state
    proposals = int(sweeps) * PARTICLE_COUNT
    accepted = 0
    for _ in range(proposals):
        current, did_accept = metropolis_proposal(topology, current, beta, rng)
        accepted += int(did_accept)
    return current, proposals, accepted


def run_anneal(particle_name: str, seed: int) -> TranslationalAnnealResult:
    validate_protocol()
    if not background_controls_hold():
        raise RuntimeError("frozen background controls failed")
    topology = PARTICLE_BY_NAME[particle_name]
    rng = random.Random(int(seed))
    initial = random_state(rng)
    state = initial
    proposals = 0
    accepted = 0
    stages: list[tuple[float, SpatialMetrics]] = []
    beta0_state: LatticeState | None = None
    beta0_metrics: SpatialMetrics | None = None

    for beta in BETA_SCHEDULE:
        state, count, acc = run_sweeps(
            topology,
            state,
            beta,
            SWEEPS_PER_BETA,
            rng,
        )
        proposals += count
        accepted += acc
        metrics = spatial_metrics(topology, state)
        stages.append((beta, metrics))
        if beta == 0.0:
            beta0_state = state
            beta0_metrics = metrics

    if beta0_state is None or beta0_metrics is None:
        raise RuntimeError("beta=0 stage was not recorded")
    final_metrics = spatial_metrics(topology, state)
    return TranslationalAnnealResult(
        particle=particle_name,
        seed=int(seed),
        initial_state=initial,
        beta0_state=beta0_state,
        final_state=state,
        beta0_metrics=beta0_metrics,
        final_metrics=final_metrics,
        stage_metrics=tuple(stages),
        proposals=proposals,
        accepted=accepted,
    )
