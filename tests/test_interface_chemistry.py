from __future__ import annotations

import unittest

from morphomatter.boundary import interpolate_config
from morphomatter.critical_surfaces import critical_frontier_coupling
from morphomatter.interface_chemistry import (
    CONTACT_ANGLES_DEG,
    THRESHOLD_SCALE,
    external_interface_c1,
    heterogeneous_shape_factor,
    interface_nucleation_config,
    interface_nucleation_point,
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


class InterfaceChemistryTests(unittest.TestCase):
    def test_protocol_angles_and_shape_factor_endpoints_are_frozen(self) -> None:
        self.assertEqual(CONTACT_ANGLES_DEG, (30.0, 60.0, 90.0, 120.0, 150.0, 180.0))
        self.assertEqual(heterogeneous_shape_factor(0.0), 0.0)
        self.assertEqual(heterogeneous_shape_factor(180.0), 1.0)
        factors = [heterogeneous_shape_factor(theta) for theta in CONTACT_ANGLES_DEG]
        self.assertEqual(factors, sorted(factors))

    def test_180_degree_exactly_reproduces_bulk_nucleation_barrier(self) -> None:
        adapted = interface_nucleation_config(HARD_CONFIG, 180.0)
        self.assertEqual(adapted, HARD_CONFIG)

    def test_c1_is_monotonic_and_scans_match(self) -> None:
        for lam in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
            roots = []
            for theta in CONTACT_ANGLES_DEG:
                point = interface_nucleation_point(config, theta)
                self.assertTrue(point.consistent)
                roots.append(point.external_root)
            self.assertEqual(roots, sorted(roots))

    def test_frontier_negative_control_is_exactly_theta_invariant(self) -> None:
        for lam in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            config = interpolate_config(EASY_CONFIG, HARD_CONFIG, lam, seed=0)
            roots = [
                critical_frontier_coupling(config, THRESHOLD_SCALE)
                for _theta in CONTACT_ANGLES_DEG
            ]
            self.assertTrue(all(root == roots[0] for root in roots))

    def test_hard_endpoint_90_degree_is_at_most_75_percent_of_180_degree(self) -> None:
        root_90 = external_interface_c1(HARD_CONFIG, 90.0)
        root_180 = external_interface_c1(HARD_CONFIG, 180.0)
        self.assertLessEqual(root_90, 0.75 * root_180)


if __name__ == "__main__":
    unittest.main()
