"""Interface-affinity / wettability surrogate for MorphoMatter Experiment 015.

A classical heterogeneous-nucleation contact-angle shape factor modifies only
local barrier values in the inner wall-adjacent shell of a frozen slab chamber.
The bulk material law and equal-flux transport field stay fixed.

This is a dimensionless research surrogate, not calibrated interface chemistry.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import ceil, cos, inf, isfinite, pi
from typing import Callable

from .core import Conditions, Phase
from .equal_flux_transport import EqualFluxField, solve_equal_flux_field
from .geometry_transport import (
    FRONTIER_SUPPORT,
    GEOMETRY_MASKS,
    PROPAGATION_DRIVE,
    THRESHOLD_SCALE,
)
from .nucleation import NucleationConfig, NucleationLattice

Cell = tuple[int, int]

CONTACT_ANGLES_DEG = (30, 60, 90, 120, 150, 180)
TARGET_FRACTION = 0.50
DRIVE_NUMERICAL_BOUNDS = (0.0, 100.0)
COUPLING_NUMERICAL_BOUNDS = (0.0, 120.0)
BISECTION_ITERATIONS = 50
ROOT_TOLERANCE = 1e-6
BULK_INVARIANCE_TOLERANCE = 1e-9


@dataclass(frozen=True)
class InterfacePartition:
    geometry: str
    interface_cells: tuple[Cell, ...]
    bulk_cells: tuple[Cell, ...]


@dataclass(frozen=True)
class InterfaceTransitionPoint:
    theta_deg: int
    mechanism: str
    analytic_root: float
    numerical_root: float | None
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


def slab_interface_partition() -> InterfacePartition:
    geometry = "slab"
    mask = GEOMETRY_MASKS[geometry]
    boundary = _boundary(mask)
    field = solve_equal_flux_field(geometry)
    evaluation = set(field.evaluation_cells)
    interface = tuple(
        sorted(
            cell
            for cell in evaluation
            if any(neighbor in boundary for neighbor in _neighbors(cell))
        )
    )
    bulk = tuple(sorted(evaluation - set(interface)))
    if not interface or not bulk:
        raise RuntimeError("interface/bulk partition is empty")
    return InterfacePartition(
        geometry=geometry,
        interface_cells=interface,
        bulk_cells=bulk,
    )


def heterogeneous_shape_factor(theta_deg: float) -> float:
    if not 0.0 <= theta_deg <= 180.0:
        raise ValueError("theta must be in [0, 180] degrees")
    theta = theta_deg * pi / 180.0
    c = cos(theta)
    return ((2.0 + c) * (1.0 - c) ** 2) / 4.0


def local_interface_barrier(config: NucleationConfig, theta_deg: float) -> float:
    return config.barrier * heterogeneous_shape_factor(theta_deg)


def _aggregate_order_statistic(roots: list[float]) -> float:
    if not roots:
        return inf
    required = ceil(TARGET_FRACTION * len(roots) - 1e-15)
    required = max(1, min(len(roots), required))
    return float(sorted(roots)[required - 1])


def _cell_values(field: EqualFluxField, cells: tuple[Cell, ...]) -> tuple[float, ...]:
    mapping = field.value_map()
    return tuple(mapping[cell] for cell in cells)


def _nucleation_root(
    config: NucleationConfig,
    local_field: float,
    local_barrier: float,
) -> float:
    if local_field <= 0.0:
        return inf
    numerator = local_barrier * THRESHOLD_SCALE - config.spontaneous_rate
    return max(0.0, numerator / (config.nucleation_drive_gain * local_field))


def _frontier_root(
    config: NucleationConfig,
    local_field: float,
    local_barrier: float,
) -> float:
    if local_field <= 0.0:
        return inf
    numerator = (
        local_barrier * THRESHOLD_SCALE
        - config.frontier_base
        - config.frontier_drive_gain * PROPAGATION_DRIVE * local_field
    )
    denominator = (
        config.frontier_neighbor_gain
        * FRONTIER_SUPPORT
        * local_field
    )
    if denominator <= 0.0:
        return inf
    return max(0.0, numerator / denominator)


def analytic_interface_c1(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: float,
) -> float:
    barrier = local_interface_barrier(config, theta_deg)
    return _aggregate_order_statistic(
        [
            _nucleation_root(config, value, barrier)
            for value in _cell_values(field, partition.interface_cells)
        ]
    )


def analytic_interface_c2(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: float,
) -> float:
    barrier = local_interface_barrier(config, theta_deg)
    return _aggregate_order_statistic(
        [
            _frontier_root(config, value, barrier)
            for value in _cell_values(field, partition.interface_cells)
        ]
    )


def analytic_bulk_c1(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
) -> float:
    return _aggregate_order_statistic(
        [
            _nucleation_root(config, value, config.barrier)
            for value in _cell_values(field, partition.bulk_cells)
        ]
    )


def _actual_probability(
    config: NucleationConfig,
    *,
    local_barrier: float,
    phase: Phase,
    support: float,
    drive: float,
    coupling: float,
) -> float:
    local_config = replace(config, barrier=local_barrier)
    model = NucleationLattice(config=local_config)
    candidate = model._transition_probability(  # noqa: SLF001 - deliberate law check
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
    values: tuple[float, ...],
    predicate: Callable[[float], bool],
) -> float:
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


def numerical_interface_c1(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: float,
) -> float | None:
    barrier = local_interface_barrier(config, theta_deg)
    values = _cell_values(field, partition.interface_cells)

    def fraction(external_drive: float) -> float:
        return _active_fraction(
            values,
            lambda local_field: _actual_probability(
                config,
                local_barrier=barrier,
                phase=Phase.DISORDERED,
                support=0.0,
                drive=external_drive * local_field,
                coupling=local_field,
            ) > 0.0,
        )

    return _bisect_target(
        fraction,
        lower=DRIVE_NUMERICAL_BOUNDS[0],
        upper=DRIVE_NUMERICAL_BOUNDS[1],
    )


def numerical_interface_c2(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: float,
) -> float | None:
    barrier = local_interface_barrier(config, theta_deg)
    values = _cell_values(field, partition.interface_cells)

    def fraction(external_coupling: float) -> float:
        return _active_fraction(
            values,
            lambda local_field: _actual_probability(
                config,
                local_barrier=barrier,
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


def numerical_bulk_c1(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
) -> float | None:
    values = _cell_values(field, partition.bulk_cells)

    def fraction(external_drive: float) -> float:
        return _active_fraction(
            values,
            lambda local_field: _actual_probability(
                config,
                local_barrier=config.barrier,
                phase=Phase.DISORDERED,
                support=0.0,
                drive=external_drive * local_field,
                coupling=local_field,
            ) > 0.0,
        )

    return _bisect_target(
        fraction,
        lower=DRIVE_NUMERICAL_BOUNDS[0],
        upper=DRIVE_NUMERICAL_BOUNDS[1],
    )


def _consistent(analytic: float, numerical: float | None, upper: float) -> bool:
    if not isfinite(analytic):
        return numerical is None
    if analytic > upper:
        return numerical is None
    return numerical is not None and abs(analytic - numerical) <= ROOT_TOLERANCE


def interface_c1_point(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: int,
) -> InterfaceTransitionPoint:
    analytic = analytic_interface_c1(config, field, partition, theta_deg)
    numerical = numerical_interface_c1(config, field, partition, theta_deg)
    return InterfaceTransitionPoint(
        theta_deg=theta_deg,
        mechanism="interface_c1_nucleation_50",
        analytic_root=analytic,
        numerical_root=numerical,
        consistent=_consistent(analytic, numerical, DRIVE_NUMERICAL_BOUNDS[1]),
    )


def interface_c2_point(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: int,
) -> InterfaceTransitionPoint:
    analytic = analytic_interface_c2(config, field, partition, theta_deg)
    numerical = numerical_interface_c2(config, field, partition, theta_deg)
    return InterfaceTransitionPoint(
        theta_deg=theta_deg,
        mechanism="interface_c2_frontier_50",
        analytic_root=analytic,
        numerical_root=numerical,
        consistent=_consistent(analytic, numerical, COUPLING_NUMERICAL_BOUNDS[1]),
    )


def bulk_c1_point(
    config: NucleationConfig,
    field: EqualFluxField,
    partition: InterfacePartition,
    theta_deg: int,
) -> InterfaceTransitionPoint:
    analytic = analytic_bulk_c1(config, field, partition)
    numerical = numerical_bulk_c1(config, field, partition)
    return InterfaceTransitionPoint(
        theta_deg=theta_deg,
        mechanism="bulk_c1_specificity_control",
        analytic_root=analytic,
        numerical_root=numerical,
        consistent=_consistent(analytic, numerical, DRIVE_NUMERICAL_BOUNDS[1]),
    )
