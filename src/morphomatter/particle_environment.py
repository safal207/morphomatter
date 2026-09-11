"""Particle-property × environment screening surrogate for Experiment 017.

A relative surface-charge-like magnitude changes only the repulsive amplitude
of the frozen Experiment 016 interaction law. Environment screening and the
attractive channel remain unchanged.

This is a synthetic dimensionless causal model, not calibrated colloid physics.
"""
from __future__ import annotations

from dataclasses import dataclass

from .environment_screening import (
    B_ACCESS,
    ROOT_I_BOUNDS,
    W_TRAP,
    _log_bisect_crossing,
    attractive_potential,
    classify_interaction_regime,
    repulsive_potential,
    screening_kappa,
    screening_length_like,
    separation_grid,
)

Q_REL_GRID = (0.60, 0.80, 1.00, 1.20, 1.40)

EXP016_ACCESS_ROOT = 0.753820427
EXP016_TRAP_ROOT = 2.502688872
ROOT_REPRO_TOLERANCE = 1e-9


@dataclass(frozen=True)
class ParticleEnvironmentMetrics:
    q_rel: float
    ionic_strength_like: float
    kappa: float
    screening_length_like: float
    barrier_height: float
    well_depth: float
    barrier_separation: float
    well_separation: float
    regime: str


def _validate_q_rel(q_rel: float) -> float:
    value = float(q_rel)
    if value <= 0.0:
        raise ValueError("q_rel must be positive")
    return value


def particle_repulsive_potential(
    separation: float,
    ionic_strength_like: float,
    q_rel: float,
) -> float:
    """Scale only the frozen Exp016 repulsive channel by q_rel squared."""
    q = _validate_q_rel(q_rel)
    return q * q * repulsive_potential(separation, ionic_strength_like)


def particle_attractive_potential(separation: float) -> float:
    """Exact frozen Experiment 016 attractive channel."""
    return attractive_potential(separation)


def particle_total_potential(
    separation: float,
    ionic_strength_like: float,
    q_rel: float,
) -> float:
    return (
        particle_repulsive_potential(separation, ionic_strength_like, q_rel)
        + particle_attractive_potential(separation)
    )


def particle_environment_metrics(
    q_rel: float,
    ionic_strength_like: float,
) -> ParticleEnvironmentMetrics:
    q = _validate_q_rel(q_rel)
    strength = float(ionic_strength_like)
    if strength <= 0.0:
        raise ValueError("ionic_strength_like must be positive")

    values = tuple(
        (h, particle_total_potential(h, strength, q))
        for h in separation_grid()
    )
    barrier_h, barrier_value = max(values, key=lambda item: item[1])
    well_h, well_value = min(values, key=lambda item: item[1])
    barrier_height = max(0.0, float(barrier_value))
    well_depth = max(0.0, -float(well_value))

    return ParticleEnvironmentMetrics(
        q_rel=q,
        ionic_strength_like=strength,
        kappa=screening_kappa(strength),
        screening_length_like=screening_length_like(strength),
        barrier_height=barrier_height,
        well_depth=well_depth,
        barrier_separation=float(barrier_h),
        well_separation=float(well_h),
        regime=classify_interaction_regime(barrier_height, well_depth),
    )


def particle_access_root(q_rel: float) -> float | None:
    q = _validate_q_rel(q_rel)
    return _log_bisect_crossing(
        lambda strength: (
            particle_environment_metrics(q, strength).barrier_height - B_ACCESS
        ),
        lower=ROOT_I_BOUNDS[0],
        upper=ROOT_I_BOUNDS[1],
        increasing=False,
    )


def particle_trap_root(q_rel: float) -> float | None:
    q = _validate_q_rel(q_rel)
    return _log_bisect_crossing(
        lambda strength: (
            particle_environment_metrics(q, strength).well_depth - W_TRAP
        ),
        lower=ROOT_I_BOUNDS[0],
        upper=ROOT_I_BOUNDS[1],
        increasing=True,
    )


def root_crossing_consistent(
    root: float | None,
    q_rel: float,
    *,
    mechanism: str,
) -> bool:
    """Independent local sign check around a solved particle-specific root."""
    if root is None:
        return False
    q = _validate_q_rel(q_rel)
    value = float(root)
    if value <= 0.0:
        return False

    lower = max(ROOT_I_BOUNDS[0], value * (1.0 - 1e-6))
    upper = min(ROOT_I_BOUNDS[1], value * (1.0 + 1e-6))

    if mechanism == "access":
        below = particle_environment_metrics(q, lower).barrier_height - B_ACCESS
        above = particle_environment_metrics(q, upper).barrier_height - B_ACCESS
        return below >= -1e-9 and above <= 1e-9
    if mechanism == "trap":
        below = particle_environment_metrics(q, lower).well_depth - W_TRAP
        above = particle_environment_metrics(q, upper).well_depth - W_TRAP
        return below <= 1e-9 and above >= -1e-9
    raise ValueError("mechanism must be 'access' or 'trap'")


def baseline_roots_reproduce_exp016() -> bool:
    access = particle_access_root(1.0)
    trap = particle_trap_root(1.0)
    if access is None or trap is None:
        return False
    return (
        abs(access - EXP016_ACCESS_ROOT)
        <= ROOT_REPRO_TOLERANCE * max(1.0, abs(EXP016_ACCESS_ROOT))
        and abs(trap - EXP016_TRAP_ROOT)
        <= ROOT_REPRO_TOLERANCE * max(1.0, abs(EXP016_TRAP_ROOT))
    )
