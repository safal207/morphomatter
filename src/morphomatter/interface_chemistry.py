"""Interface-affinity surrogate for MorphoMatter Experiment 015.

A contact-angle-like coordinate modifies only the nucleation barrier through the
classical spherical-cap heterogeneous-nucleation shape factor. Frontier and
commit laws remain untouched and serve as negative controls.

This is a causal software surrogate, not a calibrated physical wettability model.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import cos, pi

from .core import Conditions, Phase
from .critical_surfaces import classify_surface
from .nucleation import NucleationConfig, NucleationLattice

CONTACT_ANGLES_DEG = (30.0, 60.0, 90.0, 120.0, 150.0, 180.0)
THRESHOLD_SCALE = 0.80
DRIVE_SCAN = (0.00, 1.20, 0.01)
SCAN_TOLERANCE = 0.010000001
DRIVE_ENVELOPE = (0.02, 0.80)


@dataclass(frozen=True)
class InterfaceNucleationPoint:
    theta_deg: float
    shape_factor: float
    raw_root: float
    external_root: float
    classification: str
    scan_value: float | None
    consistent: bool


def heterogeneous_shape_factor(theta_deg: float) -> float:
    theta = float(theta_deg)
    if theta < 0.0 or theta > 180.0:
        raise ValueError("theta_deg must be in [0, 180]")
    c = cos(theta * pi / 180.0)
    value = ((2.0 + c) * (1.0 - c) ** 2) / 4.0
    # Stabilize exact physical endpoints against floating-point cosine noise.
    if abs(theta) < 1e-15:
        return 0.0
    if abs(theta - 180.0) < 1e-15:
        return 1.0
    return float(value)


def interface_nucleation_config(config: NucleationConfig, theta_deg: float) -> NucleationConfig:
    """Return a copy whose barrier is modified for nucleation-only queries."""
    return replace(
        config,
        barrier=config.barrier * heterogeneous_shape_factor(theta_deg),
    )


def raw_interface_c1(
    config: NucleationConfig,
    theta_deg: float,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float:
    if config.nucleation_drive_gain <= 0.0:
        raise ValueError("nucleation_drive_gain must be positive")
    factor = heterogeneous_shape_factor(theta_deg)
    return (
        config.barrier * float(threshold_scale) * factor
        - config.spontaneous_rate
    ) / config.nucleation_drive_gain


def external_interface_c1(
    config: NucleationConfig,
    theta_deg: float,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float:
    return max(0.0, raw_interface_c1(config, theta_deg, threshold_scale=threshold_scale))


def _grid(lower: float, upper: float, step: float) -> tuple[float, ...]:
    count = int(round((upper - lower) / step))
    return tuple(round(lower + i * step, 12) for i in range(count + 1))


def scan_interface_c1(
    config: NucleationConfig,
    theta_deg: float,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> float | None:
    adapted = interface_nucleation_config(config, theta_deg)
    model = NucleationLattice(config=adapted)
    lower, upper, step = DRIVE_SCAN
    for drive in _grid(lower, upper, step):
        candidate = model._transition_probability(  # noqa: SLF001 - intentional law check
            Phase.DISORDERED,
            0.0,
            Conditions(
                drive=drive,
                coupling_scale=1.0,
                threshold_scale=threshold_scale,
            ),
        )
        probability = 0.0 if candidate is None else float(candidate[1])
        if probability > 0.0:
            return drive
    return None


def _scan_consistent(raw_root: float, scan_value: float | None) -> bool:
    lower, upper, step = DRIVE_SCAN
    if raw_root <= lower:
        return scan_value is not None and scan_value <= lower + SCAN_TOLERANCE
    if raw_root > upper:
        return scan_value is None
    return (
        scan_value is not None
        and scan_value >= raw_root - 1e-9
        and scan_value - raw_root <= step + SCAN_TOLERANCE
    )


def interface_nucleation_point(
    config: NucleationConfig,
    theta_deg: float,
    *,
    threshold_scale: float = THRESHOLD_SCALE,
) -> InterfaceNucleationPoint:
    raw_root = raw_interface_c1(
        config,
        theta_deg,
        threshold_scale=threshold_scale,
    )
    external_root = max(0.0, raw_root)
    scan = scan_interface_c1(
        config,
        theta_deg,
        threshold_scale=threshold_scale,
    )
    return InterfaceNucleationPoint(
        theta_deg=float(theta_deg),
        shape_factor=heterogeneous_shape_factor(theta_deg),
        raw_root=raw_root,
        external_root=external_root,
        classification=classify_surface(external_root, *DRIVE_ENVELOPE),
        scan_value=scan,
        consistent=_scan_consistent(raw_root, scan),
    )
