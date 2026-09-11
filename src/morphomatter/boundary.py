"""Helpers for MorphoMatter Experiment 007 controllability-boundary search.

All quantities are dimensionless software controls. Interpolating two
NucleationConfig values does not imply interpolation of a real material law.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from .nucleation import NucleationConfig


_INTERPOLATED_FIELDS = (
    "spontaneous_rate",
    "nucleation_drive_gain",
    "frontier_base",
    "frontier_neighbor_gain",
    "frontier_drive_gain",
    "commit_base",
    "commit_neighbor_gain",
    "commit_drive_gain",
    "barrier",
)


def interpolate_config(
    easy: NucleationConfig,
    hard: NucleationConfig,
    lam: float,
    *,
    seed: int = 0,
) -> NucleationConfig:
    """Linearly interpolate the preregistered transition-law fields."""

    lam = float(lam)
    if not 0.0 <= lam <= 1.0:
        raise ValueError("lambda must be in [0, 1]")
    if easy.width != hard.width or easy.height != hard.height:
        raise ValueError("endpoint lattice dimensions must match")

    values = {
        field: getattr(easy, field) + lam * (getattr(hard, field) - getattr(easy, field))
        for field in _INTERPOLATED_FIELDS
    }
    return replace(easy, seed=int(seed), **values)


def config_signature(config: NucleationConfig) -> tuple[float, ...]:
    """Comparable signature for the transition-law fields only."""

    return tuple(float(getattr(config, field)) for field in _INTERPOLATED_FIELDS)


def lambda50(success_rates: Mapping[float, float]) -> float | None:
    """Largest tested lambda whose observed success rate is at least 0.50."""

    eligible = [
        float(lam)
        for lam, rate in success_rates.items()
        if float(rate) >= 0.50
    ]
    return max(eligible) if eligible else None
