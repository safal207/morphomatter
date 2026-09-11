"""Directional particle-contact topology surrogate for Experiment 018.

This module adds a normalized directional contact-allocation layer on top of the
frozen Experiment 016/017 background interaction state. It is a static contact-
graph compatibility model, not a kinetic or thermodynamic self-assembly model.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isclose
from typing import Iterable

DIRECTIONS = ("N", "E", "S", "W")
DIRECTION_INDEX = {name: index for index, name in enumerate(DIRECTIONS)}
OPPOSITE = {"N": "S", "E": "W", "S": "N", "W": "E"}
DIRECTIONAL_BUDGET = 2.0
TOLERANCE = 1e-12


@dataclass(frozen=True)
class ParticleTopology:
    name: str
    canonical_ports: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        if len(self.canonical_ports) != 4:
            raise ValueError("canonical_ports must have four cardinal weights")
        if any(value < 0.0 for value in self.canonical_ports):
            raise ValueError("port weights must be non-negative")

    @property
    def budget(self) -> float:
        return float(sum(self.canonical_ports))

    def oriented_ports(self, quarter_turns: int) -> tuple[float, float, float, float]:
        turns = int(quarter_turns) % 4
        values = self.canonical_ports
        if turns == 0:
            return values
        # Positive turns rotate N->E->S->W. A port at canonical index i moves
        # to (i + turns) mod 4.
        rotated = [0.0, 0.0, 0.0, 0.0]
        for index, value in enumerate(values):
            rotated[(index + turns) % 4] = float(value)
        return tuple(rotated)  # type: ignore[return-value]


@dataclass(frozen=True)
class ContactEdge:
    u: int
    v: int
    direction_u: str
    direction_v: str

    def __post_init__(self) -> None:
        if self.u == self.v:
            raise ValueError("self edges are not allowed")
        if self.direction_u not in DIRECTION_INDEX or self.direction_v not in DIRECTION_INDEX:
            raise ValueError("edge directions must be cardinal")
        if OPPOSITE[self.direction_u] != self.direction_v:
            raise ValueError("edge directions must be reciprocal")


@dataclass(frozen=True)
class ContactMotif:
    name: str
    node_count: int
    edges: tuple[ContactEdge, ...]
    expected_degree: int

    def degrees(self) -> tuple[int, ...]:
        degree = [0] * self.node_count
        seen: set[tuple[int, int]] = set()
        for edge in self.edges:
            if not (0 <= edge.u < self.node_count and 0 <= edge.v < self.node_count):
                raise ValueError("edge endpoint out of bounds")
            key = tuple(sorted((edge.u, edge.v)))
            if key in seen:
                raise ValueError(f"duplicate undirected edge: {key}")
            seen.add(key)
            degree[edge.u] += 1
            degree[edge.v] += 1
        return tuple(degree)

    def validate(self) -> None:
        if self.node_count <= 0:
            raise ValueError("node_count must be positive")
        degrees = self.degrees()
        if any(value != self.expected_degree for value in degrees):
            raise ValueError(
                f"{self.name} degree mismatch: expected {self.expected_degree}, got {degrees}"
            )


@dataclass(frozen=True)
class StructuralOptimum:
    particle: str
    motif: str
    edge_coverage: float
    budget_utilization: float
    total_bond_strength: float
    optimal_assignment_count: int
    canonical_orientations: tuple[int, ...]
    assignments_evaluated: int

    @property
    def score_pair(self) -> tuple[float, float]:
        return (self.edge_coverage, self.budget_utilization)


PARTICLE_TOPOLOGIES = (
    ParticleTopology("isotropic4", (0.5, 0.5, 0.5, 0.5)),
    ParticleTopology("axial2", (1.0, 0.0, 1.0, 0.0)),
    ParticleTopology("corner2", (1.0, 1.0, 0.0, 0.0)),
    ParticleTopology("tri3", (2.0 / 3.0, 2.0 / 3.0, 2.0 / 3.0, 0.0)),
)
PARTICLE_BY_NAME = {item.name: item for item in PARTICLE_TOPOLOGIES}


def _axial_ring6() -> ContactMotif:
    edges = tuple(ContactEdge(i, (i + 1) % 6, "E", "W") for i in range(6))
    return ContactMotif("axial_ring6", 6, edges, expected_degree=2)


def _corner_loop4() -> ContactMotif:
    # Node layout:
    # 0 --E-- 1
    # |        |
    # S        S
    # |        |
    # 2 --E-- 3
    edges = (
        ContactEdge(0, 1, "E", "W"),
        ContactEdge(1, 3, "S", "N"),
        ContactEdge(3, 2, "W", "E"),
        ContactEdge(2, 0, "N", "S"),
    )
    return ContactMotif("corner_loop4", 4, edges, expected_degree=2)


def _tri_ladder8() -> ContactMotif:
    # Top row: 0..3, bottom row: 4..7. Horizontal rows are periodic.
    edges: list[ContactEdge] = []
    for offset in (0, 4):
        for x in range(4):
            edges.append(ContactEdge(offset + x, offset + (x + 1) % 4, "E", "W"))
    for x in range(4):
        edges.append(ContactEdge(x, 4 + x, "S", "N"))
    return ContactMotif("tri_ladder8", 8, tuple(edges), expected_degree=3)


def _square_torus9() -> ContactMotif:
    # 3x3 torus. Add only east and south edges from every node so each
    # undirected edge appears exactly once.
    edges: list[ContactEdge] = []
    width = 3
    height = 3
    for y in range(height):
        for x in range(width):
            node = y * width + x
            east = y * width + ((x + 1) % width)
            south = ((y + 1) % height) * width + x
            edges.append(ContactEdge(node, east, "E", "W"))
            edges.append(ContactEdge(node, south, "S", "N"))
    return ContactMotif("square_torus9", 9, tuple(edges), expected_degree=4)


CONTACT_MOTIFS = (
    _axial_ring6(),
    _corner_loop4(),
    _tri_ladder8(),
    _square_torus9(),
)
MOTIF_BY_NAME = {item.name: item for item in CONTACT_MOTIFS}


def validate_frozen_protocol() -> None:
    if tuple(item.name for item in PARTICLE_TOPOLOGIES) != (
        "isotropic4",
        "axial2",
        "corner2",
        "tri3",
    ):
        raise ValueError("particle topology set drifted")
    if tuple(item.name for item in CONTACT_MOTIFS) != (
        "axial_ring6",
        "corner_loop4",
        "tri_ladder8",
        "square_torus9",
    ):
        raise ValueError("motif set drifted")
    for topology in PARTICLE_TOPOLOGIES:
        if not isclose(topology.budget, DIRECTIONAL_BUDGET, rel_tol=0.0, abs_tol=TOLERANCE):
            raise ValueError(f"directional budget drifted for {topology.name}: {topology.budget}")
    for motif in CONTACT_MOTIFS:
        motif.validate()


def bond_strength(
    topology: ParticleTopology,
    orientation_u: int,
    direction_u: str,
    orientation_v: int,
    direction_v: str,
) -> float:
    if OPPOSITE[direction_u] != direction_v:
        raise ValueError("bond directions are not reciprocal")
    ports_u = topology.oriented_ports(orientation_u)
    ports_v = topology.oriented_ports(orientation_v)
    return min(
        ports_u[DIRECTION_INDEX[direction_u]],
        ports_v[DIRECTION_INDEX[direction_v]],
    )


def evaluate_assignment(
    topology: ParticleTopology,
    motif: ContactMotif,
    orientations: tuple[int, ...],
) -> tuple[float, float, float]:
    if len(orientations) != motif.node_count:
        raise ValueError("orientation assignment size mismatch")
    covered = 0
    total = 0.0
    for edge in motif.edges:
        strength = bond_strength(
            topology,
            orientations[edge.u],
            edge.direction_u,
            orientations[edge.v],
            edge.direction_v,
        )
        if strength > 0.0:
            covered += 1
        total += strength
    coverage = covered / len(motif.edges)
    utilization = 2.0 * total / (motif.node_count * DIRECTIONAL_BUDGET)
    if utilization < -TOLERANCE or utilization > 1.0 + TOLERANCE:
        raise ValueError(
            f"budget utilization outside [0,1] for {topology.name}/{motif.name}: {utilization}"
        )
    utilization = min(1.0, max(0.0, utilization))
    return coverage, utilization, total


def exhaustive_optimum(
    topology: ParticleTopology,
    motif: ContactMotif,
) -> StructuralOptimum:
    motif.validate()
    if not isclose(topology.budget, DIRECTIONAL_BUDGET, rel_tol=0.0, abs_tol=TOLERANCE):
        raise ValueError("topology budget differs from frozen budget")

    # Technical optimization only: the search space remains exactly 4^N as
    # preregistered. Rotated port vectors and direction indices are cached so
    # each assignment evaluates only numeric lookups and min operations.
    ports_by_orientation = tuple(topology.oriented_ports(turns) for turns in range(4))
    indexed_edges = tuple(
        (
            edge.u,
            edge.v,
            DIRECTION_INDEX[edge.direction_u],
            DIRECTION_INDEX[edge.direction_v],
        )
        for edge in motif.edges
    )
    denominator = motif.node_count * DIRECTIONAL_BUDGET

    best_pair = (-1.0, -1.0)
    best_total = -1.0
    canonical: tuple[int, ...] | None = None
    optimum_count = 0
    assignments = 0

    for orientations in product(range(4), repeat=motif.node_count):
        assignments += 1
        covered = 0
        total = 0.0
        for u, v, direction_u, direction_v in indexed_edges:
            strength = min(
                ports_by_orientation[orientations[u]][direction_u],
                ports_by_orientation[orientations[v]][direction_v],
            )
            if strength > 0.0:
                covered += 1
            total += strength

        coverage = covered / len(indexed_edges)
        utilization = 2.0 * total / denominator
        if utilization < -TOLERANCE or utilization > 1.0 + TOLERANCE:
            raise ValueError(
                f"budget utilization outside [0,1] for {topology.name}/{motif.name}: {utilization}"
            )
        utilization = min(1.0, max(0.0, utilization))
        pair = (coverage, utilization)

        better = (
            coverage > best_pair[0] + TOLERANCE
            or (
                abs(coverage - best_pair[0]) <= TOLERANCE
                and utilization > best_pair[1] + TOLERANCE
            )
        )
        equal = (
            abs(coverage - best_pair[0]) <= TOLERANCE
            and abs(utilization - best_pair[1]) <= TOLERANCE
        )

        assignment = tuple(int(value) for value in orientations)
        if better:
            best_pair = pair
            best_total = total
            canonical = assignment
            optimum_count = 1
        elif equal:
            optimum_count += 1
            if canonical is None or assignment < canonical:
                canonical = assignment
            # total is determined by utilization because N and B are fixed for
            # a motif, but keep the maximum defensively.
            best_total = max(best_total, total)

    expected = 4 ** motif.node_count
    if assignments != expected:
        raise RuntimeError(f"orientation search incomplete: {assignments} != {expected}")
    if canonical is None:
        raise RuntimeError("no orientation assignment evaluated")

    return StructuralOptimum(
        particle=topology.name,
        motif=motif.name,
        edge_coverage=best_pair[0],
        budget_utilization=best_pair[1],
        total_bond_strength=best_total,
        optimal_assignment_count=optimum_count,
        canonical_orientations=canonical,
        assignments_evaluated=assignments,
    )


def full_matrix() -> tuple[StructuralOptimum, ...]:
    validate_frozen_protocol()
    return tuple(
        exhaustive_optimum(topology, motif)
        for topology in PARTICLE_TOPOLOGIES
        for motif in CONTACT_MOTIFS
    )


def preferred_motif(
    rows: Iterable[StructuralOptimum],
) -> tuple[str, bool, tuple[float, float]]:
    rows = tuple(rows)
    if not rows:
        raise ValueError("at least one row is required")
    best_coverage = max(row.edge_coverage for row in rows)
    coverage_rows = tuple(
        row for row in rows if abs(row.edge_coverage - best_coverage) <= TOLERANCE
    )
    best_utilization = max(row.budget_utilization for row in coverage_rows)
    winners = tuple(
        row
        for row in coverage_rows
        if abs(row.budget_utilization - best_utilization) <= TOLERANCE
    )
    winner = min(winners, key=lambda row: row.motif)
    return winner.motif, len(winners) == 1, (best_coverage, best_utilization)
