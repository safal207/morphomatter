"""Experiment 021: environment-driven contact-energy Monte Carlo.

This new contact-only projection samples Exp016 at h=0. It is not full DLVO,
a barrier-crossing model, or a learned controller. Static regime labels NEVER
enter the move kernel. Exp020 spatial rules and Exp018 facing ports are reused.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
import random

from .environment_screening import attractive_potential, repulsive_potential
from .particle_anisotropy import OPPOSITE, PARTICLE_BY_NAME, ParticleTopology, bond_strength
from .translational_assembly import (
    DELTAS, DIRECTIONS, GRID_SIZE, PARTICLE_COUNT, LatticeState, SpatialMetrics,
    _rotation_candidate, _translation_candidate, background_controls_hold,
    random_state, spatial_metrics,
)

TOPOLOGY_NAME = "axial2"
Q_REL = 1.0
BETA = 8.0
I_UP = (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00)
I_CYCLE = I_UP + I_UP[-2::-1]
SEEDS = tuple(range(21001, 21017))
CONTROL_SEEDS = SEEDS[:4]
SWEEP_RATES = (32, 256)
WARMUP_SWEEPS = 256
RELAXATION_SWEEPS = 512


def _positive(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result) or result <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return result


def _count(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def validate_protocol() -> None:
    if (GRID_SIZE, PARTICLE_COUNT) != (6, 8):
        raise ValueError("Exp020 spatial constants drifted")
    if TOPOLOGY_NAME != "axial2" or Q_REL != 1.0 or BETA != 8.0:
        raise ValueError("frozen particle/beta protocol drifted")
    if I_UP != (0.01, 0.03, 0.10, 0.30, 1.0, 3.0, 10.0):
        raise ValueError("environment grid drifted")
    if I_CYCLE != I_UP + I_UP[-2::-1]:
        raise ValueError("environment cycle drifted")
    if SEEDS != tuple(range(21001, 21017)) or CONTROL_SEEDS != SEEDS[:4]:
        raise ValueError("seed protocol drifted")
    if SWEEP_RATES != (32, 256) or (WARMUP_SWEEPS, RELAXATION_SWEEPS) != (256, 512):
        raise ValueError("sweep protocol drifted")
    if not background_controls_hold():
        raise RuntimeError("frozen lineage controls failed")


def energy_coefficients(strength: float, *, coupled: bool = True) -> tuple[float, float]:
    """Return (repulsive cost/contact, attractive multiplier/facing bond)."""
    label = _positive(strength, "environment coordinate")
    actual = label if coupled else 1.0
    return Q_REL ** 2 * repulsive_potential(0.0, actual), attractive_potential(0.0)


def occupied_contacts(state: LatticeState) -> tuple[tuple[int, int, str], ...]:
    """Include even directionally incompatible contacts; count each once."""
    occupancy = {position: i for i, position in enumerate(state.positions)}
    contacts = []
    for u, (x, y) in enumerate(state.positions):
        for direction in ("E", "S"):
            dx, dy = DELTAS[direction]
            v = occupancy.get(((x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE))
            if v is not None:
                contacts.append((u, v, direction))
    return tuple(contacts)


def _edge_energy(
    topology: ParticleTopology, state: LatticeState, u: int, v: int,
    direction: str, coefficients: tuple[float, float],
) -> float:
    repulsion, attraction = coefficients
    facing = bond_strength(topology, state.orientations[u], direction,
                           state.orientations[v], OPPOSITE[direction])
    return repulsion + attraction * facing


def contact_energy(
    topology: ParticleTopology, state: LatticeState, coefficients: tuple[float, float],
) -> float:
    """Independent whole-state Hamiltonian used for reporting and regression."""
    return sum(_edge_energy(topology, state, u, v, direction, coefficients)
               for u, v, direction in occupied_contacts(state))


def local_energy(
    topology: ParticleTopology, state: LatticeState, particle: int,
    coefficients: tuple[float, float],
) -> float:
    """Only edges incident to the proposed particle can change."""
    occupancy = {position: i for i, position in enumerate(state.positions)}
    x, y = state.positions[particle]
    total = 0.0
    for direction in DIRECTIONS:
        dx, dy = DELTAS[direction]
        neighbor = occupancy.get(((x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE))
        if neighbor is not None:
            total += _edge_energy(topology, state, particle, neighbor, direction, coefficients)
    return total


def metropolis_acceptance(delta_energy: float, beta: float = BETA) -> float:
    delta = float(delta_energy)
    beta_value = float(beta)
    if not isfinite(delta) or not isfinite(beta_value) or beta_value < 0.0:
        raise ValueError("energy difference and beta must be finite; beta >= 0")
    return 1.0 if delta <= 0.0 else exp(-beta_value * delta)


def proposal(
    topology: ParticleTopology, state: LatticeState,
    coefficients: tuple[float, float], rng: random.Random,
) -> tuple[LatticeState, bool]:
    particle = rng.randrange(PARTICLE_COUNT)
    if rng.randrange(2) == 0:
        candidate = _translation_candidate(state, particle, DIRECTIONS[rng.randrange(4)])
    else:
        step = -1 if rng.randrange(2) == 0 else 1
        candidate = _rotation_candidate(state, particle, step)
    # Fixed draw count also for blocked proposals and downhill moves.
    uniform = rng.random()
    if candidate is None:
        return state, False
    delta = local_energy(topology, candidate, particle, coefficients) - local_energy(
        topology, state, particle, coefficients)
    if uniform < metropolis_acceptance(delta):
        return candidate, True
    return state, False


def advance(
    topology: ParticleTopology, state: LatticeState, strength: float, sweeps: int,
    rng: random.Random, *, coupled: bool = True,
) -> tuple[LatticeState, int, int]:
    coefficients = energy_coefficients(strength, coupled=coupled)
    count = _count(sweeps, "sweeps") * PARTICLE_COUNT
    current = state
    accepted = 0
    for _ in range(count):
        current, success = proposal(topology, current, coefficients, rng)
        accepted += int(success)
    return current, count, accepted


@dataclass(frozen=True)
class CycleSnapshot:
    external_strength: float
    energy_strength: float
    state: LatticeState
    metrics: SpatialMetrics
    energy: float
    contacts: int
    proposals: int
    accepted: int

    def mechanical_key(self) -> tuple:
        """Discard the unused external label, but NOT state or energy evidence."""
        return (self.energy_strength, self.state, self.metrics, self.energy,
                self.contacts, self.proposals, self.accepted)


@dataclass(frozen=True)
class EnvironmentCycleResult:
    seed: int
    stage_sweeps: int
    coupled: bool
    initial_state: LatticeState
    stages: tuple[CycleSnapshot, ...]
    relaxed: CycleSnapshot

    def mechanical_trace(self) -> tuple:
        return (self.initial_state, tuple(s.mechanical_key() for s in self.stages),
                self.relaxed.mechanical_key())


def _snapshot(
    topology: ParticleTopology, state: LatticeState, strength: float,
    coupled: bool, proposals: int, accepted: int,
) -> CycleSnapshot:
    return CycleSnapshot(
        external_strength=float(strength), energy_strength=float(strength) if coupled else 1.0,
        state=state, metrics=spatial_metrics(topology, state),
        energy=contact_energy(topology, state, energy_coefficients(strength, coupled=coupled)),
        contacts=len(occupied_contacts(state)), proposals=proposals, accepted=accepted,
    )


def run_cycle(
    seed: int, stage_sweeps: int, *, coupled: bool = True,
    schedule: tuple[float, ...] = I_CYCLE,
) -> EnvironmentCycleResult:
    validate_protocol()
    _count(stage_sweeps, "stage_sweeps")
    if stage_sweeps == 0 or not schedule:
        raise ValueError("a nonempty schedule and positive stage_sweeps are required")
    sequence = tuple(_positive(value, "environment coordinate") for value in schedule)
    topology = PARTICLE_BY_NAME[TOPOLOGY_NAME]
    rng = random.Random(seed)
    initial = random_state(rng)
    state, proposals, accepted = advance(
        topology, initial, I_UP[0], WARMUP_SWEEPS, rng, coupled=coupled)
    snapshots = []
    for strength in sequence:
        state, count, acc = advance(topology, state, strength, stage_sweeps, rng, coupled=coupled)
        proposals += count
        accepted += acc
        snapshots.append(_snapshot(topology, state, strength, coupled, proposals, accepted))
    state, count, acc = advance(
        topology, state, I_UP[0], RELAXATION_SWEEPS, rng, coupled=coupled)
    proposals += count
    accepted += acc
    return EnvironmentCycleResult(
        seed=seed, stage_sweeps=stage_sweeps, coupled=coupled, initial_state=initial,
        stages=tuple(snapshots),
        relaxed=_snapshot(topology, state, I_UP[0], coupled, proposals, accepted),
    )
