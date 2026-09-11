"""Frozen global condition vocabulary for MorphoMatter Experiment 009.

The expanded action set strictly contains the original five recovery actions.
Every action is global: no action identifies a site, coordinate, damage pattern,
or stochastic seed. Values are dimensionless software controls.
"""
from __future__ import annotations

from .core import Conditions
from .learning import RECOVERY_ACTIONS


EXTRA_RECOVERY_ACTIONS: dict[str, Conditions] = {
    "couple_gentle": Conditions(
        drive=0.08,
        coupling_scale=1.80,
        threshold_scale=0.80,
    ),
    "couple_strong": Conditions(
        drive=0.18,
        coupling_scale=1.80,
        threshold_scale=0.80,
    ),
    "bridge_drive": Conditions(
        drive=0.38,
        coupling_scale=1.20,
        threshold_scale=0.80,
    ),
    "cooperate_low_threshold": Conditions(
        drive=0.12,
        coupling_scale=1.50,
        threshold_scale=0.70,
    ),
    "renucleate_low_threshold": Conditions(
        drive=0.55,
        coupling_scale=1.00,
        threshold_scale=0.70,
    ),
    "stabilize_high_threshold": Conditions(
        drive=0.08,
        coupling_scale=1.50,
        threshold_scale=0.90,
    ),
}


EXPANDED_RECOVERY_ACTIONS: dict[str, Conditions] = {
    **RECOVERY_ACTIONS,
    **EXTRA_RECOVERY_ACTIONS,
}


def validate_expanded_action_space() -> None:
    """Fail closed if the preregistered Experiment 009 action map drifts."""

    expected_original = ("renucleate", "cooperate", "balanced", "brute", "hold")
    expected_extra = (
        "couple_gentle",
        "couple_strong",
        "bridge_drive",
        "cooperate_low_threshold",
        "renucleate_low_threshold",
        "stabilize_high_threshold",
    )
    if tuple(RECOVERY_ACTIONS) != expected_original:
        raise RuntimeError("original recovery action set changed")
    if tuple(EXTRA_RECOVERY_ACTIONS) != expected_extra:
        raise RuntimeError("Experiment 009 extra action set changed")
    if tuple(EXPANDED_RECOVERY_ACTIONS) != expected_original + expected_extra:
        raise RuntimeError("Experiment 009 expanded action order changed")
    if len(EXPANDED_RECOVERY_ACTIONS) != 11:
        raise RuntimeError("Experiment 009 expanded action count changed")
