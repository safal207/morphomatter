import unittest

from morphomatter.boundary import interpolate_config
from morphomatter.critical_surfaces import (
    COUPLING_BOUNDS,
    DRIVE_BOUNDS,
    SCAN_TOLERANCE,
    classify_surface,
    commit_surface_point,
    critical_frontier_coupling,
    critical_nucleation_drive,
    frontier_surface_point,
    nucleation_surface_point,
    raw_frontier_propensity,
    raw_nucleation_propensity,
)
from morphomatter.nucleation import NucleationConfig


EASY_CONFIG = NucleationConfig(width=9, height=9, seed=0)
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


class CriticalSurfaceTests(unittest.TestCase):
    def test_reference_nucleation_root_is_zero_crossing(self):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)
        root = critical_nucleation_drive(config, 0.80)
        self.assertAlmostEqual(root, 0.70, places=12)
        self.assertAlmostEqual(
            raw_nucleation_propensity(
                config,
                drive=root,
                threshold_scale=0.80,
            ),
            0.0,
            places=12,
        )

    def test_reference_frontier_root_is_zero_crossing(self):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0)
        root = critical_frontier_coupling(config, 0.80)
        self.assertAlmostEqual(root, 0.6688, places=12)
        self.assertAlmostEqual(
            raw_frontier_propensity(
                config,
                coupling_scale=root,
                threshold_scale=0.80,
            ),
            0.0,
            places=12,
        )

    def test_scans_recover_in_envelope_roots_with_frozen_tolerance(self):
        for lam in (0.0, 0.4, 0.8, 1.0):
            config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam)
            for threshold in (0.70, 0.80, 0.90):
                for point in (
                    nucleation_surface_point(config, threshold),
                    frontier_surface_point(config, threshold),
                    commit_surface_point(config, threshold),
                ):
                    self.assertTrue(point.consistent)
                    if point.classification == "IN_ENVELOPE":
                        self.assertIsNotNone(point.scan_value)
                        self.assertLessEqual(
                            abs(point.scan_value - point.critical_value),
                            SCAN_TOLERANCE,
                        )

    def test_classification_uses_frozen_control_envelopes(self):
        self.assertEqual(
            classify_surface(DRIVE_BOUNDS[0] - 0.01, *DRIVE_BOUNDS),
            "BELOW_ENVELOPE",
        )
        self.assertEqual(
            classify_surface(DRIVE_BOUNDS[1] + 0.01, *DRIVE_BOUNDS),
            "ABOVE_ENVELOPE",
        )
        self.assertEqual(
            classify_surface(sum(COUPLING_BOUNDS) / 2.0, *COUPLING_BOUNDS),
            "IN_ENVELOPE",
        )


if __name__ == "__main__":
    unittest.main()
