"""Critical transition-surface helpers for MorphoMatter Experiment 011.

These functions characterize zero crossings of the existing synthetic
NucleationLattice law. They do not define physical phase boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .core import Conditions, Phase
from .nucleation import NucleationConfig, NucleationLattice


FRONTIER_NEIGHBOR_FRACTION = 0.25
PROPAGATION_DRIVE = 0.12
DRIVE_BOUNDS = (0.02, 0.80)
COUPLING_BOUNDS = (0.00, 1.80)
SCAN_STEP = 0.01
SCAN_TOLERANCE = 0.010000001


@dataclass(frozen=True)
class SurfacePoint:
    mechanism: str
    critical_value: float
    classification: str
    scan_value: float | None
    consistent: bool


def classify_surface(value: float, lower: float, upper: float) -> str:
    value = float(value)
    if value < lower:
        return "BELOW_ENVELOPE"
    if value > upper:
        return "ABOVE_ENVELOPE"
    return "IN_ENVELOPE"


def raw_nucleation_propensity(
    config: NucleationConfig,
    *,
    drive: float,
    threshold_scale: float,
) -> float:
    return (
        config.spontaneous_rate
        + config.nucleation_drive_gain * float(drive)
        - config.barrier * float(threshold_scale)
    )


def raw_frontier_propensity(
    config: NucleationConfig,
    *,
    coupling_scale: float,
    threshold_scale: float,
    drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_NEIGHBOR_FRACTION,
) -> float:
    return (
        config.frontier_base
        + config.frontier_neighbor_gain
        * float(ordered_neighbor_fraction)
        * float(coupling_scale)
        + config.frontier_drive_gain * float(drive)
        - config.barrier * float(threshold_scale)
    )


def raw_commit_propensity(
    config: NucleationConfig,
    *,
    coupling_scale: float,
    threshold_scale: float,
    drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_NEIGHBOR_FRACTION,
) -> float:
    return (
        config.commit_base
        + config.commit_neighbor_gain
        * float(ordered_neighbor_fraction)
        * float(coupling_scale)
        + config.commit_drive_gain * float(drive)
        - config.barrier * float(threshold_scale)
    )


def critical_nucleation_drive(
    config: NucleationConfig,
    threshold_scale: float,
) -> float:
    if config.nucleation_drive_gain <= 0:
        raise ValueError("nucleation_drive_gain must be positive")
    return (
        config.barrier * float(threshold_scale) - config.spontaneous_rate
    ) / config.nucleation_drive_gain


def critical_frontier_coupling(
    config: NucleationConfig,
    threshold_scale: float,
    *,
    drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_NEIGHBOR_FRACTION,
) -> float:
    denominator = config.frontier_neighbor_gain * float(ordered_neighbor_fraction)
    if denominator <= 0:
        raise ValueError("frontier neighbor gain and support must be positive")
    return (
        config.barrier * float(threshold_scale)
        - config.frontier_base
        - config.frontier_drive_gain * float(drive)
    ) / denominator


def critical_commit_coupling(
    config: NucleationConfig,
    threshold_scale: float,
    *,
    drive: float = PROPAGATION_DRIVE,
    ordered_neighbor_fraction: float = FRONTIER_NEIGHBOR_FRACTION,
) -> float:
    denominator = config.commit_neighbor_gain * float(ordered_neighbor_fraction)
    if denominator <= 0:
        raise ValueError("commit neighbor gain and support must be positive")
    return (
        config.barrier * float(threshold_scale)
        - config.commit_base
        - config.commit_drive_gain * float(drive)
    ) / denominator


def _grid(lower: float, upper: float, step: float) -> tuple[float, ...]:
    if step <= 0:
        raise ValueError("step must be positive")
    count = int(round((upper - lower) / step))
    return tuple(round(lower + index * step, 12) for index in range(count + 1))


def _first_positive(
    values: tuple[float, ...],
    probability: Callable[[float], float],
) -> float | None:
    for value in values:
        if probability(value) > 0.0:
            return value
    return None


def _actual_probability(
    config: NucleationConfig,
    *,
    phase: Phase,
    ordered_neighbor_fraction: float,
    conditions: Conditions,
) -> float:
    model = NucleationLattice(config=config)
    candidate = model._transition_probability(  # noqa: SLF001 - intentional law check
        phase,
        ordered_neighbor_fraction,
        conditions,
    )
    if candidate is None:
        return 0.0
    return float(candidate[1])


def scan_nucleation_onset(
    config: NucleationConfig,
    threshold_scale: float,
) -> float | None:
    values = _grid(DRIVE_BOUNDS[0], DRIVE_BOUNDS[1], SCAN_STEP)
    return _first_positive(
        values,
        lambda drive: _actual_probability(
            config,
            phase=Phase.DISORDERED,
            ordered_neighbor_fraction=0.0,
            conditions=Conditions(
                drive=drive,
                coupling_scale=1.0,
                threshold_scale=threshold_scale,
            ),
        ),
    )


def scan_frontier_onset(
    config: NucleationConfig,
    threshold_scale: float,
) -> float | None:
    values = _grid(COUPLING_BOUNDS[0], COUPLING_BOUNDS[1], SCAN_STEP)
    return _first_positive(
        values,
        lambda coupling: _actual_probability(
            config,
            phase=Phase.DISORDERED,
            ordered_neighbor_fraction=FRONTIER_NEIGHBOR_FRACTION,
            conditions=Conditions(
                drive=PROPAGATION_DRIVE,
                coupling_scale=coupling,
                threshold_scale=threshold_scale,
            ),
        ),
    )


def scan_commit_onset(
    config: NucleationConfig,
    threshold_scale: float,
) -> float | None:
    values = _grid(COUPLING_BOUNDS[0], COUPLING_BOUNDS[1], SCAN_STEP)
    return _first_positive(
        values,
        lambda coupling: _actual_probability(
            config,
            phase=Phase.METASTABLE,
            ordered_neighbor_fraction=FRONTIER_NEIGHBOR_FRACTION,
            conditions=Conditions(
                drive=PROPAGATION_DRIVE,
                coupling_scale=coupling,
                threshold_scale=threshold_scale,
            ),
        ),
    )


def _scan_consistent(
    critical_value: float,
    classification: str,
    scan_value: float | None,
    *,
    lower: float,
) -> bool:
    if classification == "IN_ENVELOPE":
        return (
            scan_value is not None
            and abs(float(scan_value) - float(critical_value)) <= SCAN_TOLERANCE
        )
    if classification == "BELOW_ENVELOPE":
        return (
            scan_value is not None
            and float(scan_value) <= lower + SCAN_TOLERANCE
        )
    if classification == "ABOVE_ENVELOPE":
        return scan_value is None
    raise ValueError(f"unknown classification: {classification}")


def nucleation_surface_point(
    config: NucleationConfig,
    threshold_scale: float,
) -> SurfacePoint:
    critical = critical_nucleation_drive(config, threshold_scale)
    classification = classify_surface(critical, *DRIVE_BOUNDS)
    scan = scan_nucleation_onset(config, threshold_scale)
    return SurfacePoint(
        mechanism="nucleation",
        critical_value=critical,
        classification=classification,
        scan_value=scan,
        consistent=_scan_consistent(
            critical,
            classification,
            scan,
            lower=DRIVE_BOUNDS[0],
        ),
    )


def frontier_surface_point(
    config: NucleationConfig,
    threshold_scale: float,
) -> SurfacePoint:
    critical = critical_frontier_coupling(config, threshold_scale)
    classification = classify_surface(critical, *COUPLING_BOUNDS)
    scan = scan_frontier_onset(config, threshold_scale)
    return SurfacePoint(
        mechanism="frontier",
        critical_value=critical,
        classification=classification,
        scan_value=scan,
        consistent=_scan_consistent(
            critical,
            classification,
            scan,
            lower=COUPLING_BOUNDS[0],
        ),
    )


def commit_surface_point(
    config: NucleationConfig,
    threshold_scale: float,
) -> SurfacePoint:
    critical = critical_commit_coupling(config, threshold_scale)
    classification = classify_surface(critical, *COUPLING_BOUNDS)
    scan = scan_commit_onset(config, threshold_scale)
    return SurfacePoint(
        mechanism="commit",
        critical_value=critical,
        classification=classification,
        scan_value=scan,
        consistent=_scan_consistent(
            critical,
            classification,
            scan,
            lower=COUPLING_BOUNDS[0],
        ),
    )
