"""Solved spatial transport field for MorphoMatter Experiment 013.

A deterministic discrete Laplace problem is solved on each frozen chamber mask.
The resulting field scales local drive/coupling before the unchanged synthetic
NucleationLattice transition law is queried. This is not calibrated physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf, isfinite
from statistics import median
from typing import Callable

from .core import Conditions, Phase
from .critical_surfaces import classify_surface
from .geometry_transport import (
    COUPLING_ENVELOPE,
    DRIVE_ENVELOPE,
    FRONTIER_SUPPORT,
    GEOMETRY_MASKS,
    PROPAGATION_DRIVE,
    THRESHOLD_SCALE,
)
from .nucleation import NucleationConfig, NucleationLattice

Cell = tuple[int, int]

FIELD_TOLERANCE = 1e-10
FIELD_MAX_ITERATIONS = 20_000
TARGET_FRACTION = 0.50
DRIVE_NUMERICAL_BOUNDS = (0.0, 20.0)
COUPLING_NUMERICAL_BOUNDS = (0.0, 30.0)
BISECTION_ITERATIONS = 40
ROOT_TOLERANCE = 1e-6
MIN_CORE_CELLS = 20


@dataclass(frozen=True)
class PDEField:
    geometry: str
    source_cells: tuple[Cell, ...]
    sink_cells: tuple[Cell, ...]
    core_cells: tuple[Cell, ...]
    values: tuple[tuple[Cell, float], ...]
    iterations: int
    residual: float

    def value_map(self) -> dict[Cell, float]:
        return dict(self.values)

    def core_values(self) -> tuple[float, ...]:
        mapping = self.value_map()
        return tuple(mapping[cell] for cell in self.core_cells)

    @property
    def mean_core(self) -> float:
        values = self.core_values()
        return sum(values) / len(values)

    @property
    def median_core(self) -> float:
        return float(median(self.core_values()))

    @property
    def min_core(self) -> float:
        return min(self.core_values())

    @property
    def max_core(self) -> float:
        return max(self.core_values())


@dataclass(frozen=True)
class PDETransitionPoint:
    geometry: str
    mechanism: str
    analytic_root: float
    numerical_root: float | None
    classification: str
    consistent: bool


def _neighbors(cell: Cell) -> tuple[Cell, ...]:
    row, col = cell
    return (
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    )


def _boundary(mask: frozenset[Cell]) -> frozenset[Cell]:
    return frozenset(
        cell for cell in mask if any(neighbor not in mask for neighbor in _neighbors(cell))
    )


def solve_laplace_field(
    geometry: str,
    *,
    tolerance: float = FIELD_TOLERANCE,
    max_iterations: int = FIELD_MAX_ITERATIONS,
) -> PDEField:
    if geometry not in GEOMETRY_MASKS:
        raise KeyError(geometry)
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    mask = GEOMETRY_MASKS[geometry]
    boundary = _boundary(mask)
    minimum_row = min(row for row, _ in mask)
    source = frozenset(cell for cell in mask if cell[0] == minimum_row)
    sink = boundary - source
    core = tuple(sorted(mask - boundary))
    if len(core) < MIN_CORE_CELLS:
        raise RuntimeError(f"geometry {geometry} has too few core cells")
    if not source:
        raise RuntimeError(f"geometry {geometry} has no source cells")

    values = {cell: (1.0 if cell in source else 0.0) for cell in mask}
    residual = inf

    for iteration in range(1, max_iterations + 1):
        next_values = values.copy()
        max_update = 0.0
        for cell in core:
            active_neighbors = tuple(n for n in _neighbors(cell) if n in mask)
            if len(active_neighbors) != 4:
                raise RuntimeError("core cell unexpectedly touches chamber exterior")
            new_value = sum(values[n] for n in active_neighbors) / 4.0
            max_update = max(max_update, abs(new_value - values[cell]))
            next_values[cell] = new_value
        for cell in source:
            next_values[cell] = 1.0
        for cell in sink:
            next_values[cell] = 0.0
        values = next_values
        residual = max_update
        if max_update < tolerance:
            break
    else:
        raise RuntimeError(f"Laplace solve did not converge for {geometry}")

    harmonic_residual = 0.0
    for cell in core:
        expected = sum(values[n] for n in _neighbors(cell)) / 4.0
        harmonic_residual = max(harmonic_residual, abs(values[cell] - expected))

    return PDEField(
        geometry=geometry,
        source_cells=tuple(sorted(source)),
        sink_cells=tuple(sorted(sink)),
        core_cells=core,
        values=tuple(sorted(values.items())),
        iterations=iteration,
        residual=harmonic_residual,
    )


def all_pde_fields() -> tuple[PDEField, ...]:
    return tuple(solve_laplace_field(name) for name in GEOMETRY_MASKS)


def _aggregate_order_statistic(roots: list[float], fraction: float = TARGET_FRACTION) -> float:
    if not roots:
        return inf
    required = ceil(fraction * len(roots) - 1e-15)
    required = max(1, min(len(roots), required))
    ordered = sorted(roots)
    return float(ordered[required - 1])


def analytic_pde_c1(
    config: NucleationConfig,
    field: PDEField,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float:
    local_base = (
        config.barrier * threshold_scale - config.spontaneous_rate
    ) / config.nucleation_drive_gain
    roots: list[float] = []
    for value in field.core_values():
        if value <= 0.0:
            roots.append(inf)
        else:
            roots.append(max(0.0, local_base / value))
    return _aggregate_order_statistic(roots)


def analytic_pde_c2(
    config: NucleationConfig,
    field: PDEField,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
    external_drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_SUPPORT,
) -> float:
    roots: list[float] = []
    for value in field.core_values():
        if value <= 0.0:
            roots.append(inf)
            continue
        numerator = (
            config.barrier * threshold_scale
            - config.frontier_base
            - config.frontier_drive_gain * external_drive * value
        )
        denominator = (
            config.frontier_neighbor_gain
            * ordered_neighbor_fraction
            * value
        )
        if denominator <= 0.0:
            roots.append(inf)
        else:
            roots.append(max(0.0, numerator / denominator))
    return _aggregate_order_statistic(roots)


def _actual_probability(
    config: NucleationConfig,
    *,
    phase: Phase,
    support: float,
    drive: float,
    coupling: float,
) -> float:
    model = NucleationLattice(config=config)
    candidate = model._transition_probability(  # noqa: SLF001 - intentional law check
        phase,
        support,
        Conditions(
            drive=drive,
            coupling_scale=coupling,
            threshold_scale=THRESHOLD_SCALE,
        ),
    )
    return 0.0 if candidate is None else float(candidate[1])


def _active_fraction(field: PDEField, predicate: Callable[[float], bool]) -> float:
    values = field.core_values()
    return sum(predicate(value) for value in values) / len(values)


def _bisect_target(
    active_fraction: Callable[[float], float],
    *,
    lower: float,
    upper: float,
) -> float | None:
    if active_fraction(lower) >= TARGET_FRACTION:
        return lower
    if active_fraction(upper) < TARGET_FRACTION:
        return None
    lo = lower
    hi = upper
    for _ in range(BISECTION_ITERATIONS):
        mid = (lo + hi) / 2.0
        if active_fraction(mid) >= TARGET_FRACTION:
            hi = mid
        else:
            lo = mid
    return hi


def numerical_pde_c1(config: NucleationConfig, field: PDEField) -> float | None:
    def fraction(external_drive: float) -> float:
        return _active_fraction(
            field,
            lambda local_field: _actual_probability(
                config,
                phase=Phase.DISORDERED,
                support=0.0,
                drive=external_drive * local_field,
                coupling=1.0 * local_field,
            ) > 0.0,
        )

    return _bisect_target(
        fraction,
        lower=DRIVE_NUMERICAL_BOUNDS[0],
        upper=DRIVE_NUMERICAL_BOUNDS[1],
    )


def numerical_pde_c2(config: NucleationConfig, field: PDEField) -> float | None:
    def fraction(external_coupling: float) -> float:
        return _active_fraction(
            field,
            lambda local_field: _actual_probability(
                config,
                phase=Phase.DISORDERED,
                support=FRONTIER_SUPPORT,
                drive=PROPAGATION_DRIVE * local_field,
                coupling=external_coupling * local_field,
            ) > 0.0,
        )

    return _bisect_target(
        fraction,
        lower=COUPLING_NUMERICAL_BOUNDS[0],
        upper=COUPLING_NUMERICAL_BOUNDS[1],
    )


def _consistent(
    analytic: float,
    numerical: float | None,
    numerical_upper: float,
) -> bool:
    if not isfinite(analytic):
        return numerical is None
    if analytic > numerical_upper:
        return numerical is None
    return numerical is not None and abs(analytic - numerical) <= ROOT_TOLERANCE


def pde_c1_point(config: NucleationConfig, field: PDEField) -> PDETransitionPoint:
    analytic = analytic_pde_c1(config, field)
    numerical = numerical_pde_c1(config, field)
    classification = (
        "ABOVE_ENVELOPE"
        if not isfinite(analytic)
        else classify_surface(analytic, *DRIVE_ENVELOPE)
    )
    return PDETransitionPoint(
        geometry=field.geometry,
        mechanism="pde_c1_nucleation_50",
        analytic_root=analytic,
        numerical_root=numerical,
        classification=classification,
        consistent=_consistent(analytic, numerical, DRIVE_NUMERICAL_BOUNDS[1]),
    )


def pde_c2_point(config: NucleationConfig, field: PDEField) -> PDETransitionPoint:
    analytic = analytic_pde_c2(config, field)
    numerical = numerical_pde_c2(config, field)
    classification = (
        "ABOVE_ENVELOPE"
        if not isfinite(analytic)
        else classify_surface(analytic, *COUPLING_ENVELOPE)
    )
    return PDETransitionPoint(
        geometry=field.geometry,
        mechanism="pde_c2_frontier_50",
        analytic_root=analytic,
        numerical_root=numerical,
        classification=classification,
        consistent=_consistent(analytic, numerical, COUPLING_NUMERICAL_BOUNDS[1]),
    )
