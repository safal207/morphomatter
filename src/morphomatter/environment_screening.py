"""Environment-chemistry screened-interaction surrogate for Experiment 016.

The environment coordinate changes only an electrostatic-repulsion-like channel.
A short-range attractive channel is fixed. The resulting pair-potential metrics
are used to classify a synthetic assembly regime. This is not calibrated DLVO
physics and all coordinates/energies are dimensionless.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, log, sqrt
from typing import Callable

IONIC_STRENGTH_GRID = (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00)

REPULSION_AMPLITUDE = 3.0
ATTRACTION_DEPTH = 1.0
ATTRACTION_RANGE = 0.18
KAPPA_SCALE = 1.0

H_MIN = 0.0
H_MAX = 3.0
H_STEP = 0.0025

B_ACCESS = 0.50
W_MIN = 0.15
W_TRAP = 0.55

ROOT_I_BOUNDS = (0.001, 100.0)
ROOT_ITERATIONS = 60
ROOT_REL_TOLERANCE = 1e-10


@dataclass(frozen=True)
class InteractionMetrics:
    ionic_strength_like: float
    kappa: float
    screening_length_like: float
    barrier_height: float
    well_depth: float
    barrier_separation: float
    well_separation: float
    regime: str


def screening_kappa(ionic_strength_like: float) -> float:
    value = float(ionic_strength_like)
    if value <= 0.0:
        raise ValueError("ionic_strength_like must be positive")
    return KAPPA_SCALE * sqrt(value)


def screening_length_like(ionic_strength_like: float) -> float:
    return 1.0 / screening_kappa(ionic_strength_like)


def repulsive_potential(separation: float, ionic_strength_like: float) -> float:
    h = float(separation)
    if h < 0.0:
        raise ValueError("separation must be non-negative")
    kappa = screening_kappa(ionic_strength_like)
    amplitude = REPULSION_AMPLITUDE / (1.0 + kappa) ** 2
    return amplitude * exp(-kappa * h)


def attractive_potential(separation: float) -> float:
    h = float(separation)
    if h < 0.0:
        raise ValueError("separation must be non-negative")
    return -ATTRACTION_DEPTH * exp(-h / ATTRACTION_RANGE)


def total_potential(separation: float, ionic_strength_like: float) -> float:
    return repulsive_potential(separation, ionic_strength_like) + attractive_potential(separation)


def separation_grid() -> tuple[float, ...]:
    count = int(round((H_MAX - H_MIN) / H_STEP))
    return tuple(round(H_MIN + i * H_STEP, 12) for i in range(count + 1))


def classify_interaction_regime(barrier_height: float, well_depth: float) -> str:
    barrier = float(barrier_height)
    well = float(well_depth)
    if barrier > B_ACCESS:
        return "DISPERSED_BARRIER"
    if well < W_MIN:
        return "ACCESSIBLE_BUT_WEAK"
    if well <= W_TRAP:
        return "REVERSIBLE_ASSEMBLY"
    return "KINETIC_TRAP_RISK"


def interaction_metrics(ionic_strength_like: float) -> InteractionMetrics:
    strength = float(ionic_strength_like)
    values = tuple((h, total_potential(h, strength)) for h in separation_grid())
    barrier_h, barrier_value = max(values, key=lambda item: item[1])
    well_h, well_value = min(values, key=lambda item: item[1])
    barrier_height = max(0.0, float(barrier_value))
    well_depth = max(0.0, -float(well_value))
    return InteractionMetrics(
        ionic_strength_like=strength,
        kappa=screening_kappa(strength),
        screening_length_like=screening_length_like(strength),
        barrier_height=barrier_height,
        well_depth=well_depth,
        barrier_separation=float(barrier_h),
        well_separation=float(well_h),
        regime=classify_interaction_regime(barrier_height, well_depth),
    )


def all_grid_metrics() -> tuple[InteractionMetrics, ...]:
    return tuple(interaction_metrics(value) for value in IONIC_STRENGTH_GRID)


def _log_bisect_crossing(
    signed_value: Callable[[float], float],
    *,
    lower: float = ROOT_I_BOUNDS[0],
    upper: float = ROOT_I_BOUNDS[1],
    increasing: bool,
) -> float | None:
    if lower <= 0.0 or upper <= lower:
        raise ValueError("invalid positive root bounds")
    f_lo = float(signed_value(lower))
    f_hi = float(signed_value(upper))

    if increasing:
        if f_lo >= 0.0:
            return lower
        if f_hi < 0.0:
            return None
    else:
        if f_lo <= 0.0:
            return lower
        if f_hi > 0.0:
            return None

    log_lo = log(lower)
    log_hi = log(upper)
    for _ in range(ROOT_ITERATIONS):
        log_mid = (log_lo + log_hi) / 2.0
        mid = exp(log_mid)
        f_mid = float(signed_value(mid))
        if increasing:
            if f_mid >= 0.0:
                log_hi = log_mid
            else:
                log_lo = log_mid
        else:
            if f_mid <= 0.0:
                log_hi = log_mid
            else:
                log_lo = log_mid
    return exp(log_hi)


def access_root() -> float | None:
    """I where the interaction barrier first becomes <= B_ACCESS."""
    return _log_bisect_crossing(
        lambda strength: interaction_metrics(strength).barrier_height - B_ACCESS,
        increasing=False,
    )


def trap_root() -> float | None:
    """I where the well depth first becomes >= W_TRAP."""
    return _log_bisect_crossing(
        lambda strength: interaction_metrics(strength).well_depth - W_TRAP,
        increasing=True,
    )


def crossing_is_consistent(root: float | None, signed_value: Callable[[float], float], *, increasing: bool) -> bool:
    if root is None:
        return False
    root = float(root)
    if root <= 0.0:
        return False
    below = max(ROOT_I_BOUNDS[0], root * (1.0 - 1e-6))
    above = min(ROOT_I_BOUNDS[1], root * (1.0 + 1e-6))
    f_below = float(signed_value(below))
    f_above = float(signed_value(above))
    if increasing:
        return f_below <= ROOT_REL_TOLERANCE and f_above >= -ROOT_REL_TOLERANCE
    return f_below >= -ROOT_REL_TOLERANCE and f_above <= ROOT_REL_TOLERANCE
