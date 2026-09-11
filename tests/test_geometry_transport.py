import unittest

from morphomatter.boundary import interpolate_config
from morphomatter.geometry_transport import (
    AREA_TOLERANCE,
    GEOMETRY_MASKS,
    REFERENCE_AREA,
    all_geometry_metrics,
    geometry_frontier_surface_point,
    geometry_nucleation_surface_point,
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


class GeometryTransportTests(unittest.TestCase):
    def test_frozen_geometry_names_and_areas(self):
        self.assertEqual(
            tuple(GEOMETRY_MASKS),
            (
                "slab",
                "cylinder_like",
                "pyramid_like",
                "concave_hourglass",
                "meandering_channel",
            ),
        )
        metrics = {m.name: m for m in all_geometry_metrics()}
        self.assertEqual(metrics["slab"].area, 225)
        self.assertEqual(metrics["cylinder_like"].area, 225)
        self.assertEqual(metrics["pyramid_like"].area, 220)
        self.assertEqual(metrics["concave_hourglass"].area, 213)
        self.assertEqual(metrics["meandering_channel"].area, 231)
        for item in metrics.values():
            self.assertLessEqual(
                abs(item.area - REFERENCE_AREA) / REFERENCE_AREA,
                AREA_TOLERANCE + 1e-12,
            )

    def test_slab_is_exact_gain_reference(self):
        slab = {m.name: m for m in all_geometry_metrics()}["slab"]
        self.assertAlmostEqual(slab.drive_gain, 1.0)
        self.assertAlmostEqual(slab.coupling_gain, 1.0)

    def test_geometry_gains_are_derived_not_special_cased(self):
        metrics = {m.name: m for m in all_geometry_metrics()}
        self.assertGreater(metrics["cylinder_like"].drive_gain, 1.0)
        self.assertLess(metrics["pyramid_like"].drive_gain, 1.0)
        self.assertLess(metrics["concave_hourglass"].drive_gain, 1.0)
        self.assertLess(metrics["meandering_channel"].drive_gain, 1.0)

    def test_analytic_roots_match_actual_transition_law_scans(self):
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0, seed=0)
        for metrics in all_geometry_metrics():
            nucleation = geometry_nucleation_surface_point(config, metrics)
            frontier = geometry_frontier_surface_point(config, metrics)
            self.assertTrue(nucleation.consistent, metrics.name)
            self.assertTrue(frontier.consistent, metrics.name)


if __name__ == "__main__":
    unittest.main()
