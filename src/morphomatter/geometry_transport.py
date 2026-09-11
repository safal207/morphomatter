"""Geometry-derived transport surrogate for MorphoMatter Experiment 012.

Geometry affects only delivered global conditions through transparent geometric
proxies. The underlying NucleationLattice transition law is unchanged.
This is not a calibrated physical transport model or evidence of a pyramid effect.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import sqrt

from .core import Conditions, Phase
from .critical_surfaces import classify_surface
from .nucleation import NucleationConfig, NucleationLattice

GRID_SIZE = 21
REFERENCE_AREA = 225
AREA_TOLERANCE = 0.06
THRESHOLD_SCALE = 0.80
FRONTIER_SUPPORT = 0.25
PROPAGATION_DRIVE = 0.12
DRIVE_ENVELOPE = (0.02, 0.80)
COUPLING_ENVELOPE = (0.00, 1.80)
DRIVE_SCAN = (0.02, 1.20, 0.01)
COUPLING_SCAN = (0.00, 2.50, 0.01)
SCAN_TOLERANCE = 0.010000001

Cell = tuple[int, int]


@dataclass(frozen=True)
class GeometryMetrics:
    name: str
    area: int
    boundary_cells: int
    mean_wall_distance: float
    mean_connectivity: float
    drive_gain: float
    coupling_gain: float


@dataclass(frozen=True)
class GeometrySurfacePoint:
    geometry: str
    mechanism: str
    critical_external_value: float
    classification: str
    scan_value: float | None
    consistent: bool


def _slab_mask() -> frozenset[Cell]:
    return frozenset((r, c) for r in range(3, 18) for c in range(3, 18))


def _cylinder_like_mask() -> frozenset[Cell]:
    center = 10
    radius = 8.5
    return frozenset(
        (r, c)
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
        if (r - center) ** 2 + (c - center) ** 2 <= radius**2
    )


def _pyramid_like_mask() -> frozenset[Cell]:
    cells: set[Cell] = set()
    for r in range(1, 21):
        half = int(round((r - 1) / 19 * 10))
        cells.update((r, c) for c in range(10 - half, 10 + half + 1))
    return frozenset(cells)


def _concave_hourglass_mask() -> frozenset[Cell]:
    cells: set[Cell] = set()
    for r in range(GRID_SIZE):
        d = abs(r - 10) / 10
        half = 2 + int(round(d * 5))
        cells.update((r, c) for c in range(10 - half, 10 + half + 1))
    return frozenset(cells)


def _meandering_channel_mask() -> frozenset[Cell]:
    cells: set[Cell] = set()
    for r in range(GRID_SIZE):
        if 5 <= r < 10:
            center = 13
        elif 10 <= r < 15:
            center = 7
        else:
            center = 10
        cells.update((r, c) for c in range(center - 5, center + 6))
    return frozenset(cells)


GEOMETRY_MASKS: dict[str, frozenset[Cell]] = {
    "slab": _slab_mask(),
    "cylinder_like": _cylinder_like_mask(),
    "pyramid_like": _pyramid_like_mask(),
    "concave_hourglass": _concave_hourglass_mask(),
    "meandering_channel": _meandering_channel_mask(),
}


def _neighbors(cell: Cell) -> tuple[Cell, ...]:
    r, c = cell
    return ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))


def _boundary(mask: frozenset[Cell]) -> frozenset[Cell]:
    return frozenset(cell for cell in mask if any(n not in mask for n in _neighbors(cell)))


def _is_connected(mask: frozenset[Cell]) -> bool:
    if not mask:
        return False
    seen = {next(iter(mask))}
    queue = deque(seen)
    while queue:
        cell = queue.popleft()
        for neighbor in _neighbors(cell):
            if neighbor in mask and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == len(mask)


def _wall_distances(mask: frozenset[Cell]) -> dict[Cell, int]:
    boundary = _boundary(mask)
    distance = {cell: 0 for cell in boundary}
    queue = deque(boundary)
    while queue:
        cell = queue.popleft()
        for neighbor in _neighbors(cell):
            if neighbor in mask and neighbor not in distance:
                distance[neighbor] = distance[cell] + 1
                queue.append(neighbor)
    if len(distance) != len(mask):
        raise RuntimeError("geometry mask is disconnected")
    return distance


def _raw_geometry_metrics(name: str) -> tuple[int, int, float, float]:
    mask = GEOMETRY_MASKS[name]
    if not _is_connected(mask):
        raise RuntimeError(f"geometry {name} is not connected")
    area = len(mask)
    if abs(area - REFERENCE_AREA) / REFERENCE_AREA > AREA_TOLERANCE + 1e-12:
        raise RuntimeError(f"geometry {name} violates frozen area tolerance")
    boundary = _boundary(mask)
    distances = _wall_distances(mask)
    mean_wall_distance = sum(distances.values()) / area
    mean_connectivity = sum(
        sum(neighbor in mask for neighbor in _neighbors(cell)) / 4.0
        for cell in mask
    ) / area
    return area, len(boundary), mean_wall_distance, mean_connectivity


def all_geometry_metrics() -> tuple[GeometryMetrics, ...]:
    raw = {name: _raw_geometry_metrics(name) for name in GEOMETRY_MASKS}
    _, _, slab_distance, slab_connectivity = raw["slab"]
    result: list[GeometryMetrics] = []
    for name in GEOMETRY_MASKS:
        area, boundary_cells, wall_distance, connectivity = raw[name]
        drive_gain = (1.0 + wall_distance) / (1.0 + slab_distance)
        degree_ratio = connectivity / slab_connectivity
        coupling_gain = sqrt(drive_gain * degree_ratio)
        result.append(
            GeometryMetrics(
                name=name,
                area=area,
                boundary_cells=boundary_cells,
                mean_wall_distance=wall_distance,
                mean_connectivity=connectivity,
                drive_gain=drive_gain,
                coupling_gain=coupling_gain,
            )
        )
    return tuple(result)


def geometry_metrics(name: str) -> GeometryMetrics:
    return {metrics.name: metrics for metrics in all_geometry_metrics()}[name]


def adapt_conditions(conditions: Conditions, metrics: GeometryMetrics) -> Conditions:
    return Conditions(
        drive=conditions.drive * metrics.drive_gain,
        coupling_scale=conditions.coupling_scale * metrics.coupling_gain,
        threshold_scale=conditions.threshold_scale,
    )


def critical_external_nucleation_drive(
    config: NucleationConfig,
    metrics: GeometryMetrics,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float:
    denominator = config.nucleation_drive_gain * metrics.drive_gain
    if denominator <= 0:
        raise ValueError("effective nucleation gain must be positive")
    return (config.barrier * threshold_scale - config.spontaneous_rate) / denominator


def critical_external_frontier_coupling(
    config: NucleationConfig,
    metrics: GeometryMetrics,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
    external_drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_SUPPORT,
) -> float:
    denominator = (
        config.frontier_neighbor_gain
        * ordered_neighbor_fraction
        * metrics.coupling_gain
    )
    if denominator <= 0:
        raise ValueError("effective frontier coupling gain must be positive")
    effective_drive = external_drive * metrics.drive_gain
    return (
        config.barrier * threshold_scale
        - config.frontier_base
        - config.frontier_drive_gain * effective_drive
    ) / denominator


def _grid(lower: float, upper: float, step: float) -> tuple[float, ...]:
    count = int(round((upper - lower) / step))
    return tuple(round(lower + index * step, 12) for index in range(count + 1))


def _actual_probability(
    config: NucleationConfig,
    *,
    phase: Phase,
    ordered_neighbor_fraction: float,
    external_conditions: Conditions,
    metrics: GeometryMetrics,
) -> float:
    model = NucleationLattice(config=config)
    candidate = model._transition_probability(  # noqa: SLF001 - intentional law check
        phase,
        ordered_neighbor_fraction,
        adapt_conditions(external_conditions, metrics),
    )
    return 0.0 if candidate is None else float(candidate[1])


def _first_positive(values: tuple[float, ...], fn) -> float | None:
    for value in values:
        if fn(value) > 0.0:
            return value
    return None


def scan_external_nucleation_drive(
    config: NucleationConfig,
    metrics: GeometryMetrics,
) -> float | None:
    lower, upper, step = DRIVE_SCAN
    return _first_positive(
        _grid(lower, upper, step),
        lambda drive: _actual_probability(
            config,
            phase=Phase.DISORDERED,
            ordered_neighbor_fraction=0.0,
            external_conditions=Conditions(
                drive=drive,
                coupling_scale=1.0,
                threshold_scale=THRESHOLD_SCALE,
            ),
            metrics=metrics,
        ),
    )


def scan_external_frontier_coupling(
    config: NucleationConfig,
    metrics: GeometryMetrics,
) -> float | None:
    lower, upper, step = COUPLING_SCAN
    return _first_positive(
        _grid(lower, upper, step),
        lambda coupling: _actual_probability(
            config,
            phase=Phase.DISORDERED,
            ordered_neighbor_fraction=FRONTIER_SUPPORT,
            external_conditions=Conditions(
                drive=PROPAGATION_DRIVE,
                coupling_scale=coupling,
                threshold_scale=THRESHOLD_SCALE,
            ),
            metrics=metrics,
        ),
    )


def _consistent(critical: float, scan: float | None, measurement_bounds: tuple[float, float, float]) -> bool:
    lower, upper, step = measurement_bounds
    if critical < lower:
        return scan is not None and scan <= lower + SCAN_TOLERANCE
    if critical > upper:
        return scan is None
    return (
        scan is not None
        and scan >= critical - 1e-9
        and scan - critical <= step + SCAN_TOLERANCE
    )


def geometry_nucleation_surface_point(
    config: NucleationConfig,
    metrics: GeometryMetrics,
) -> GeometrySurfacePoint:
    critical = critical_external_nucleation_drive(config, metrics)
    scan = scan_external_nucleation_drive(config, metrics)
    return GeometrySurfacePoint(
        geometry=metrics.name,
        mechanism="nucleation",
        critical_external_value=critical,
        classification=classify_surface(critical, *DRIVE_ENVELOPE),
        scan_value=scan,
        consistent=_consistent(critical, scan, DRIVE_SCAN),
    )


def geometry_frontier_surface_point(
    config: NucleationConfig,
    metrics: GeometryMetrics,
) -> GeometrySurfacePoint:
    critical = critical_external_frontier_coupling(config, metrics)
    scan = scan_external_frontier_coupling(config, metrics)
    return GeometrySurfacePoint(
        geometry=metrics.name,
        mechanism="frontier",
        critical_external_value=critical,
        classification=classify_surface(critical, *COUPLING_ENVELOPE),
        scan_value=scan,
        consistent=_consistent(critical, scan, COUPLING_SCAN),
    )
