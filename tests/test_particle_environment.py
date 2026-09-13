from __future__ import annotations

import unittest

from morphomatter.environment_screening import (
    IONIC_STRENGTH_GRID,
    attractive_potential,
    interaction_metrics,
)
from morphomatter.particle_environment import (
    Q_REL_GRID,
    baseline_roots_reproduce_exp016,
    particle_attractive_potential,
    particle_environment_metrics,
    particle_repulsive_potential,
)


class ParticleEnvironmentTests(unittest.TestCase):
    def test_protocol_particle_grid_is_frozen(self) -> None:
        self.assertEqual(Q_REL_GRID, (0.60, 0.80, 1.00, 1.20, 1.40))

    def test_q_one_exactly_reproduces_exp016_grid_metrics(self) -> None:
        for strength in IONIC_STRENGTH_GRID:
            baseline = interaction_metrics(strength)
            candidate = particle_environment_metrics(1.0, strength)
            self.assertAlmostEqual(candidate.barrier_height, baseline.barrier_height, places=12)
            self.assertAlmostEqual(candidate.well_depth, baseline.well_depth, places=12)
            self.assertAlmostEqual(candidate.barrier_separation, baseline.barrier_separation, places=12)
            self.assertAlmostEqual(candidate.well_separation, baseline.well_separation, places=12)
            self.assertEqual(candidate.regime, baseline.regime)

    def test_q_one_reproduces_exp016_continuous_roots(self) -> None:
        self.assertTrue(baseline_roots_reproduce_exp016())

    def test_attractive_channel_is_exactly_particle_and_environment_invariant(self) -> None:
        for separation in (0.0, 0.10, 0.50, 1.0, 2.0, 3.0):
            expected = attractive_potential(separation)
            self.assertEqual(particle_attractive_potential(separation), expected)
            for _q in Q_REL_GRID:
                for _strength in IONIC_STRENGTH_GRID:
                    self.assertEqual(particle_attractive_potential(separation), expected)

    def test_screening_coordinates_depend_only_on_environment(self) -> None:
        for strength in IONIC_STRENGTH_GRID:
            metrics = [particle_environment_metrics(q, strength) for q in Q_REL_GRID]
            kappas = {round(item.kappa, 15) for item in metrics}
            lengths = {round(item.screening_length_like, 15) for item in metrics}
            self.assertEqual(len(kappas), 1)
            self.assertEqual(len(lengths), 1)

    def test_repulsion_amplitude_scales_as_q_squared(self) -> None:
        separation = 0.4
        strength = 1.0
        baseline = particle_repulsive_potential(separation, strength, 1.0)
        for q in Q_REL_GRID:
            observed = particle_repulsive_potential(separation, strength, q)
            self.assertAlmostEqual(observed, q * q * baseline, places=12)

    def test_nonpositive_particle_coordinate_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            particle_environment_metrics(0.0, 1.0)
        with self.assertRaises(ValueError):
            particle_repulsive_potential(0.2, 1.0, -1.0)


if __name__ == "__main__":
    unittest.main()
