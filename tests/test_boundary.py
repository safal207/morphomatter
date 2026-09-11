import unittest

from morphomatter.boundary import config_signature, interpolate_config, lambda50
from morphomatter.nucleation import NucleationConfig


class BoundaryHelpersTests(unittest.TestCase):
    def test_interpolation_preserves_endpoints(self):
        easy = NucleationConfig(seed=9)
        hard = NucleationConfig(
            seed=10,
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
        left = interpolate_config(easy, hard, 0.0, seed=0)
        right = interpolate_config(easy, hard, 1.0, seed=0)
        self.assertEqual(config_signature(left), config_signature(easy))
        self.assertEqual(config_signature(right), config_signature(hard))
        self.assertEqual(left.seed, 0)
        self.assertEqual(right.seed, 0)

    def test_interpolation_midpoint_is_linear(self):
        easy = NucleationConfig(spontaneous_rate=0.02, barrier=0.10)
        hard = NucleationConfig(spontaneous_rate=0.002, barrier=0.16)
        middle = interpolate_config(easy, hard, 0.5)
        self.assertAlmostEqual(middle.spontaneous_rate, 0.011)
        self.assertAlmostEqual(middle.barrier, 0.13)

    def test_lambda50_returns_largest_passing_grid_point(self):
        rates = {0.0: 1.0, 0.2: 0.9, 0.4: 0.5, 0.6: 0.49, 0.8: 0.1}
        self.assertEqual(lambda50(rates), 0.4)
        self.assertIsNone(lambda50({0.0: 0.49, 0.2: 0.1}))


if __name__ == "__main__":
    unittest.main()
