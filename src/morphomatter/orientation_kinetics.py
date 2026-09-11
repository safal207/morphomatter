"""Orientation-only stochastic kinetics for MorphoMatter Experiment 019.

The Experiment 018 contact graph is held fixed. Only quarter-turn particle
orientations evolve through a local Metropolis-like proposal kernel. This is a
synthetic finite-state kinetic surrogate, not Brownian or thermodynamic physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isclose
import random

from .particle_anisotropy import (
    CONTACT_MOTIFS,
    MOTIF_BY_NAME,
    PARTICLE_BY_NAME,
    PARTICLE_TOPOLOGIES,
    ContactMotif,
    ParticleTopology,
    evaluate_assignment,
    exhaustive_optimum,
    preferred_motif,
    validate_frozen_protocol,
)

BETA_SLOW = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
BETA_FAST = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)
BETA_FAST_REVERSE = (4.0, 2.0, 1.0, 0.5, 0.0)
SLOW_SWEEPS_PER_BETA = 120
FAST_SWEEPS_PER_BETA = 2
RELAX_SWEEPS_AT_ZERO = 30
SEEDS = tuple(range(17001, 17033))
UTILIZATION_WEIGHT = 0.01
QUALITY_COVERAGE_WEIGHT = 0.99
QUALITY_UTILIZATION_WEIGHT = 0.01

MATCHED_PAIRS = (
    ("isotropic4", "square_torus9"),
    ("axial2", "axial_ring6"),
    ("corner2", "corner_loop4"),
    ("tri3", "tri_ladder8"),
)


@dataclass(frozen=True)
class AssignmentMetrics:
    edge_coverage: float
    budget_utilization: float
    covered_edges: int
    kinetic_score: float
    quality: float


@dataclass(frozen=True)
class SlowAnnealResult:
    particle: str
    motif: str
    seed: int
    initial: tuple[int, ...]
    final: tuple[int, ...]
    final_metrics: AssignmentMetrics
    success: bool
    proposals: int
    accepted: int


@dataclass(frozen=True)
class FastCycleResult:
    particle: str
    motif: str
    seed: int
    initial: tuple[int, ...]
    initial_quality: float
    forward_quality: tuple[tuple[float, float], ...]
    reverse_quality: tuple[tuple[float, float], ...]
    relaxed_quality: float
    final_relaxed: tuple[int, ...]
    proposals: int
    accepted: int


def validate_protocol() -> None:
    validate_frozen_protocol()
    if BETA_SLOW != (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        raise ValueError("BETA_SLOW drifted")
    if BETA_FAST != (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        raise ValueError("BETA_FAST drifted")
    if BETA_FAST_REVERSE != (4.0, 2.0, 1.0, 0.5, 0.0):
        raise ValueError("BETA_FAST_REVERSE drifted")
    if SLOW_SWEEPS_PER_BETA != 120 or FAST_SWEEPS_PER_BETA != 2:
        raise ValueError("sweep protocol drifted")
    if RELAX_SWEEPS_AT_ZERO != 30:
        raise ValueError("zero-beta relax protocol drifted")
    if SEEDS != tuple(range(17001, 17033)):
        raise ValueError("seed set drifted")
    if MATCHED_PAIRS != (
        ("isotropic4", "square_torus9"),
        ("axial2", "axial_ring6"),
        ("corner2", "corner_loop4"),
        ("tri3", "tri_ladder8"),
    ):
        raise ValueError("matched pairs drifted")


def assignment_metrics(
    topology: ParticleTopology,
    motif: ContactMotif,
    orientations: tuple[int, ...],
) -> AssignmentMetrics:
    coverage, utilization, _total = evaluate_assignment(topology, motif, orientations)
    covered_float = coverage * len(motif.edges)
    covered = int(round(covered_float))
    if not isclose(covered_float, covered, rel_tol=0.0, abs_tol=1e-10):
        raise RuntimeError("coverage is not an integral edge count")
    kinetic_score = covered + UTILIZATION_WEIGHT * utilization
    quality = (
        QUALITY_COVERAGE_WEIGHT * coverage
        + QUALITY_UTILIZATION_WEIGHT * utilization
    )
    return AssignmentMetrics(
        edge_coverage=coverage,
        budget_utilization=utilization,
        covered_edges=covered,
        kinetic_score=kinetic_score,
        quality=quality,
    )


def random_orientations(rng: random.Random, node_count: int) -> tuple[int, ...]:
    return tuple(rng.randrange(4) for _ in range(node_count))


def _proposal_orientation(rng: random.Random, current: int) -> int:
    candidates = tuple(value for value in range(4) if value != current)
    return candidates[rng.randrange(3)]


def metropolis_proposal(
    topology: ParticleTopology,
    motif: ContactMotif,
    orientations: tuple[int, ...],
    beta: float,
    rng: random.Random,
) -> tuple[tuple[int, ...], bool]:
    beta_value = float(beta)
    if beta_value < 0.0:
        raise ValueError("beta must be non-negative")
    node = rng.randrange(motif.node_count)
    proposed = list(orientations)
    proposed[node] = _proposal_orientation(rng, orientations[node])
    candidate = tuple(proposed)

    current_score = assignment_metrics(topology, motif, orientations).kinetic_score
    new_score = assignment_metrics(topology, motif, candidate).kinetic_score
    delta = new_score - current_score
    if delta >= 0.0:
        return candidate, True
    probability = exp(beta_value * delta)
    if probability < 0.0 or probability > 1.0 + 1e-12:
        raise RuntimeError("invalid Metropolis acceptance probability")
    if rng.random() < min(1.0, probability):
        return candidate, True
    return orientations, False


def run_sweeps(
    topology: ParticleTopology,
    motif: ContactMotif,
    orientations: tuple[int, ...],
    beta: float,
    sweeps: int,
    rng: random.Random,
) -> tuple[tuple[int, ...], int, int]:
    if sweeps < 0:
        raise ValueError("sweeps must be non-negative")
    state = tuple(orientations)
    proposals = int(sweeps) * motif.node_count
    accepted = 0
    for _ in range(proposals):
        state, did_accept = metropolis_proposal(topology, motif, state, beta, rng)
        accepted += int(did_accept)
    return state, proposals, accepted


def run_slow_anneal(particle_name: str, motif_name: str, seed: int) -> SlowAnnealResult:
    validate_protocol()
    topology = PARTICLE_BY_NAME[particle_name]
    motif = MOTIF_BY_NAME[motif_name]
    rng = random.Random(int(seed))
    initial = random_orientations(rng, motif.node_count)
    state = initial
    proposals = 0
    accepted = 0
    for beta in BETA_SLOW:
        state, count, acc = run_sweeps(
            topology,
            motif,
            state,
            beta,
            SLOW_SWEEPS_PER_BETA,
            rng,
        )
        proposals += count
        accepted += acc
    metrics = assignment_metrics(topology, motif, state)
    success = (
        abs(metrics.edge_coverage - 1.0) <= 1e-12
        and metrics.budget_utilization >= 0.95 - 1e-12
    )
    return SlowAnnealResult(
        particle=particle_name,
        motif=motif_name,
        seed=int(seed),
        initial=initial,
        final=state,
        final_metrics=metrics,
        success=success,
        proposals=proposals,
        accepted=accepted,
    )


def run_fast_cycle(particle_name: str, motif_name: str, seed: int) -> FastCycleResult:
    validate_protocol()
    topology = PARTICLE_BY_NAME[particle_name]
    motif = MOTIF_BY_NAME[motif_name]
    rng = random.Random(int(seed))
    initial = random_orientations(rng, motif.node_count)
    state = initial
    initial_quality = assignment_metrics(topology, motif, state).quality
    forward: list[tuple[float, float]] = []
    reverse: list[tuple[float, float]] = []
    proposals = 0
    accepted = 0

    for beta in BETA_FAST:
        state, count, acc = run_sweeps(
            topology,
            motif,
            state,
            beta,
            FAST_SWEEPS_PER_BETA,
            rng,
        )
        proposals += count
        accepted += acc
        forward.append((beta, assignment_metrics(topology, motif, state).quality))

    for beta in BETA_FAST_REVERSE:
        state, count, acc = run_sweeps(
            topology,
            motif,
            state,
            beta,
            FAST_SWEEPS_PER_BETA,
            rng,
        )
        proposals += count
        accepted += acc
        reverse.append((beta, assignment_metrics(topology, motif, state).quality))

    state, count, acc = run_sweeps(
        topology,
        motif,
        state,
        0.0,
        RELAX_SWEEPS_AT_ZERO,
        rng,
    )
    proposals += count
    accepted += acc
    relaxed_quality = assignment_metrics(topology, motif, state).quality

    return FastCycleResult(
        particle=particle_name,
        motif=motif_name,
        seed=int(seed),
        initial=initial,
        initial_quality=initial_quality,
        forward_quality=tuple(forward),
        reverse_quality=tuple(reverse),
        relaxed_quality=relaxed_quality,
        final_relaxed=state,
        proposals=proposals,
        accepted=accepted,
    )


def static_controls_hold() -> bool:
    """Verify the four Experiment 018 preferred motifs and perfect optima."""
    validate_protocol()
    rows = []
    for topology in PARTICLE_TOPOLOGIES:
        topology_rows = [
            exhaustive_optimum(topology, motif)
            for motif in CONTACT_MOTIFS
        ]
        preferred, unique, pair = preferred_motif(topology_rows)
        expected = dict(MATCHED_PAIRS)[topology.name]
        rows.append(
            unique
            and preferred == expected
            and abs(pair[0] - 1.0) <= 1e-12
            and abs(pair[1] - 1.0) <= 1e-12
        )
    return all(rows)
