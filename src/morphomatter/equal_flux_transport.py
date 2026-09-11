"""Equal-total-flux transport surrogate for MorphoMatter Experiment 014.

Each frozen chamber mask receives the same total graph source flux. The solved
potential field then scales local drive/coupling before the unchanged synthetic
NucleationLattice law is queried. This is not calibrated physical transport.
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

Q_TOTAL = 1.0
FIELD_TOLERANCE = 1e-10
FIELD_MAX_ITERATIONS = 30_000
CONSERVATION_TOLERANCE = 1e-7
TARGET_FRACTION = 0.50
DRIVE_NUMERICAL_BOUNDS = (0.0, 50.0)
COUPLING_NUMERICAL_BOUNDS = (0.0, 60.0)
BISECTION_ITERATIONS = 50
ROOT_TOLERANCE = 1e-6
MIN_EVALUATION_CELLS = 20


@dataclass(frozen=True)
class EqualFluxField:
    geometry: str
    source_cells: tuple[Cell, ...]
    sink_cells: tuple[Cell, ...]
    evaluation_cells: tuple[Cell, ...]
    values: tuple[tuple[Cell, float], ...]
    injection_per_source: float
    total_injection: float
    sink_flux: float
    iterations: int
    residual: float

    def value_map(self) -> dict[Cell, float]:
        return dict(self.values)

    def evaluation_values(self) -> tuple[float, ...]:
        mapping = self.value_map()
        return tuple(mapping[cell] for cell in self.evaluation_cells)

    @property
    def mean_evaluation(self) -> float:
        values = self.evaluation_values()
        return sum(values) / len(values)

    @property
    def median_evaluation(self) -> float:
        return float(median(self.evaluation_values()))

    @property
    def min_evaluation(self) -> float:
        return min(self.evaluation_values())

    @property
    def max_evaluation(self) -> float:
        return max(self.evaluation_values())


@dataclass(frozen=True)
class EqualFluxTransitionPoint:
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


def solve_equal_flux_field(
    geometry: str,
    *,
    q_total: float = Q_TOTAL,
    tolerance: float = FIELD_TOLERANCE,
    max_iterations: int = FIELD_MAX_ITERATIONS,
) -> EqualFluxField:
    if geometry not in GEOMETRY_MASKS:
        raise KeyError(geometry)
    if q_total <= 0:
        raise ValueError("q_total must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")

    mask = GEOMETRY_MASKS[geometry]
    boundary = _boundary(mask)
    minimum_row = min(row for row, _ in mask)
    source = frozenset(cell for cell in mask if cell[0] == minimum_row)
    sink = boundary - source
    unknown = tuple(sorted(mask - sink))
    evaluation = tuple(sorted(mask - boundary))

    if not source:
        raise RuntimeError(f"geometry {geometry} has no source cells")
    if not sink:
        raise RuntimeError(f"geometry {geometry} has no sink cells")
    if len(evaluation) < MIN_EVALUATION_CELLS:
        raise RuntimeError(f"geometry {geometry} has too few evaluation cells")

    injection_per_source = q_total / len(source)
    injection = {
        cell: (injection_per_source if cell in source else 0.0)
        for cell in unknown
    }
    values = {cell: 0.0 for cell in mask}

    # Deterministic Gauss-Seidel fixed-point solve for the graph-Poisson system.
    residual = inf
    for iteration in range(1, max_iterations + 1):
        max_update = 0.0
        for cell in unknown:
            active_neighbors = tuple(n for n in _neighbors(cell) if n in mask)
            degree = len(active_neighbors)
            if degree <= 0:
                raise RuntimeError(f"isolated active cell in {geometry}: {cell}")
            new_value = (
                injection[cell] + sum(values[n] for n in active_neighbors)
            ) / degree
            max_update = max(max_update, abs(new_value - values[cell]))
            values[cell] = new_value
        for cell in sink:
            values[cell] = 0.0
        if max_update < tolerance:
            break
    else:
        raise RuntimeError(f"equal-flux solve did not converge for {geometry}")

    equation_residual = 0.0
    for cell in unknown:
        active_neighbors = tuple(n for n in _neighbors(cell) if n in mask)
        degree = len(active_neighbors)
        lhs = degree * values[cell] - sum(values[n] for n in active_neighbors)
        equation_residual = max(equation_residual, abs(lhs - injection[cell]))

    sink_flux = 0.0
    for sink_cell in sink:
        for neighbor in _neighbors(sink_cell):
            if neighbor in mask and neighbor not in sink:
                sink_flux += values[neighbor]

    if equation_residual > max(1e-8, tolerance * 100):
        raise RuntimeError(
            f"equal-flux residual too large for {geometry}: {equation_residual}"
        )
    if abs(sink_flux - q_total) > CONSERVATION_TOLERANCE:
        raise RuntimeError(
            f"equal-flux conservation failed for {geometry}: "
            f"sink={sink_flux} source={q_total}"
        )

    return EqualFluxField(
        geometry=geometry,
        source_cells=tuple(sorted(source)),
        sink_cells=tuple(sorted(sink)),
        evaluation_cells=evaluation,
        values=tuple(sorted(values.items())),
        injection_per_source=injection_per_source,
        total_injection=q_total,
        sink_flux=sink_flux,
        iterations=iteration,
        residual=equation_residual,
    )


def all_equal_flux_fields() -> tuple[EqualFluxField, ...]:
    return tuple(solve_equal_flux_field(name) for name in GEOMETRY_MASKS)


def _aggregate_order_statistic(
    roots: list[float],
    fraction: float = TARGET_FRACTION,
) -> float:
    if not roots:
        return inf
    required = ceil(fraction * len(roots) - 1e-15)
    required = max(1, min(len(roots), required))
    return float(sorted(roots)[required - 1])


def analytic_equal_flux_c1(
    config: NucleationConfig,
    field: EqualFluxField,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float:
    local_base = (
        config.barrier * threshold_scale - config.spontaneous_rate
    ) / config.nucleation_drive_gain
    roots: list[float] = []
    for value in field.evaluation_values():
        roots.append(inf if value <= 0.0 else max(0.0, local_base / value))
    return _aggregate_order_statistic(roots)


def analytic_equal_flux_c2(
    config: NucleationConfig,
    field: EqualFluxField,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
    external_drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_SUPPORT,
) -> float:
    roots: list[float] = []
    for value in field.evaluation_values():
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
        roots.append(inf if denominator <= 0.0 else max(0.0, numerator / denominator))
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


def _active_fraction(
    field: EqualFluxField,
    predicate: Callable[[float], bool],
) -> float:
    values = field.evaluation_values()
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


def numerical_equal_flux_c1(
    config: NucleationConfig,
    field: EqualFluxField,
) -> float | None:
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


def numerical_equal_flux_c2(
    config: NucleationConfig,
    field: EqualFluxField,
) -> float | None:
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


def equal_flux_c1_point(
    config: NucleationConfig,
    field: EqualFluxField,
) -> EqualFluxTransitionPoint:
    analytic = analytic_equal_flux_c1(config, field)
    numerical = numerical_equal_flux_c1(config, field)
    classification = (
        "ABOVE_ENVELOPE"
        if not isfinite(analytic)
        else classify_surface(analytic, *DRIVE_ENVELOPE)
    )
    return EqualFluxTransitionPoint(
        geometry=field.geometry,
        mechanism="equal_flux_c1_nucleation_50",
        analytic_root=analytic,
        numerical_root=numerical,
        classification=classification,
        consistent=_consistent(analytic, numerical, DRIVE_NUMERICAL_BOUNDS[1]),
    )


def equal_flux_c2_point(
    config: NucleationConfig,
    field: EqualFluxField,
) -> EqualFluxTransitionPoint:
    analytic = analytic_equal_flux_c2(config, field)
    numerical = numerical_equal_flux_c2(config, field)
    classification = (
        "ABOVE_ENVELOPE"
        if not isfinite(analytic)
        else classify_surface(analytic, *COUPLING_ENVELOPE)
    )
    return EqualFluxTransitionPoint(
        geometry=field.geometry,
        mechanism="equal_flux_c2_frontier_50",
        analytic_root=analytic,
        numerical_root=numerical,
        classification=classification,
        consistent=_consistent(analytic, numerical, COUPLING_NUMERICAL_BOUNDS[1]),
    )
