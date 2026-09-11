from __future__ import annotations

import unittest

from morphomatter.environment_screening import (
    ATTRACTION_DEPTH,
    ATTRACTION_RANGE,
    B_ACCESS,
    H_MAX,
    H_MIN,
    H_STEP,
    IONIC_STRENGTH_GRID,
    KAPPA_SCALE,
    REPULSION_AMPLITUDE,
    ROOT_I_BOUNDS,
    ROOT_ITERATIONS,
    W_MIN,
    W_TRAP,
    _log_bisect_crossing,
    attractive_potential,
    classify_interaction_regime,
    interaction_metrics,
    screening_kappa,
    screening_length_like,
)
from morphomatter.interface_chemistry import external_interface_c1
from morphomatter.nucleation import NucleationConfig


HARD_CONFIG = NucleationConfig(
    width=9,
    height=9,
    seed=0,
    spontaneous_rate=0.002,
    nucleation_drive_gain=0.18,
    frontier_base=0.03,
    frontier_neighbor_gain=0.50,
    frontier_drive_gain=0.12,
    commit_base=0.14,
    commit_neighbor_gain=0.30,
    commit_drive_gain=0.25,
    barrier=0.16,
)


class EnvironmentScreeningTests(unittest.TestCase):
    def test_protocol_constants_are_frozen(self) -> None:
        self.assertEqual(IONIC_STRENGTH_GRID, (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00))
        self.assertEqual(REPULSION_AMPLITUDE, 3.0)
        self.assertEqual(ATTRACTION_DEPTH, 1.0)
        self.assertEqual(ATTRACTION_RANGE, 0.18)
        self.assertEqual(KAPPA_SCALE, 1.0)
        self.assertEqual((H_MIN, H_MAX, H_STEP), (0.0, 3.0, 0.0025))
        self.assertEqual((B_ACCESS, W_MIN, W_TRAP), (0.50, 0.15, 0.55))
        self.assertEqual(ROOT_I_BOUNDS, (0.001, 100.0))
        self.assertEqual(ROOT_ITERATIONS, 60)

    def test_screening_length_decreases_with_environment_coordinate(self) -> None:
        kappas = [screening_kappa(value) for value in IONIC_STRENGTH_GRID]
        lengths = [screening_length_like(value) for value in IONIC_STRENGTH_GRID]
        self.assertEqual(kappas, sorted(kappas))
        self.assertEqual(lengths, sorted(lengths, reverse=True))

    def test_attractive_channel_is_environment_independent(self) -> None:
        samples = [attractive_potential(h) for h in (0.0, 0.1, 0.5, 1.0)]
        repeated = [attractive_potential(h) for h in (0.0, 0.1, 0.5, 1.0)]
        self.assertEqual(samples, repeated)

    def test_log_bisection_recovers_artificial_crossings(self) -> None:
        decreasing = _log_bisect_crossing(
            lambda x: 2.0 - x,
            lower=0.1,
            upper=10.0,
            increasing=False,
        )
        increasing = _log_bisect_crossing(
            lambda x: x - 3.0,
            lower=0.1,
            upper=10.0,
            increasing=True,
        )
        self.assertIsNotNone(decreasing)
        self.assertIsNotNone(increasing)
        self.assertAlmostEqual(float(decreasing), 2.0, places=8)
        self.assertAlmostEqual(float(increasing), 3.0, places=8)

    def test_regime_classifier_boundaries(self) -> None:
        self.assertEqual(classify_interaction_regime(0.6, 0.3), "DISPERSED_BARRIER")
        self.assertEqual(classify_interaction_regime(0.4, 0.1), "ACCESSIBLE_BUT_WEAK")
        self.assertEqual(classify_interaction_regime(0.4, 0.3), "REVERSIBLE_ASSEMBLY")
        self.assertEqual(classify_interaction_regime(0.4, 0.8), "KINETIC_TRAP_RISK")

    def test_metrics_are_deterministic(self) -> None:
        first = interaction_metrics(1.0)
        second = interaction_metrics(1.0)
        self.assertEqual(first, second)

    def test_interface_nucleation_negative_control_is_environment_independent(self) -> None:
        control = external_interface_c1(HARD_CONFIG, 180.0)
        self.assertAlmostEqual(control, 0.700000000, places=9)
        for _strength in IONIC_STRENGTH_GRID:
            self.assertAlmostEqual(external_interface_c1(HARD_CONFIG, 180.0), control, places=12)


if __name__ == "__main__":
    unittest.main()
