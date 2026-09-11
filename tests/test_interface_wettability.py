from __future__ import annotations

import unittest

from morphomatter.boundary import interpolate_config
from morphomatter.equal_flux_transport import solve_equal_flux_field
from morphomatter.interface_wettability import (
    BULK_INVARIANCE_TOLERANCE,
    CONTACT_ANGLES_DEG,
    analytic_bulk_c1,
    analytic_interface_c1,
    bulk_c1_point,
    heterogeneous_shape_factor,
    interface_c1_point,
    interface_c2_point,
    slab_interface_partition,
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


class InterfaceWettabilityTests(unittest.TestCase):
    def test_classical_shape_factor_is_frozen_and_monotonic(self) -> None:
        self.assertEqual(CONTACT_ANGLES_DEG, (30, 60, 90, 120, 150, 180))
        factors = [heterogeneous_shape_factor(theta) for theta in CONTACT_ANGLES_DEG]
        self.assertTrue(all(a < b for a, b in zip(factors, factors[1:])))
        self.assertAlmostEqual(heterogeneous_shape_factor(90), 0.5, places=12)
        self.assertAlmostEqual(heterogeneous_shape_factor(180), 1.0, places=12)

    def test_interface_partition_is_fixed_and_disjoint(self) -> None:
        partition = slab_interface_partition()
        self.assertGreater(len(partition.interface_cells), 0)
        self.assertGreater(len(partition.bulk_cells), 0)
        self.assertFalse(set(partition.interface_cells) & set(partition.bulk_cells))
        field = solve_equal_flux_field("slab")
        self.assertEqual(
            set(partition.interface_cells) | set(partition.bulk_cells),
            set(field.evaluation_cells),
        )

    def test_hard_endpoint_roots_match_actual_law(self) -> None:
        field = solve_equal_flux_field("slab")
        partition = slab_interface_partition()
        for theta in (30, 90, 180):
            c1 = interface_c1_point(HARD_CONFIG, field, partition, theta)
            c2 = interface_c2_point(HARD_CONFIG, field, partition, theta)
            bulk = bulk_c1_point(HARD_CONFIG, field, partition, theta)
            self.assertTrue(c1.consistent)
            self.assertTrue(c2.consistent)
            self.assertTrue(bulk.consistent)

    def test_bulk_control_is_invariant_while_interface_c1_moves(self) -> None:
        field = solve_equal_flux_field("slab")
        partition = slab_interface_partition()
        config = interpolate_config(EASY_CONFIG, HARD_CONFIG, 1.0, seed=0)
        bulk_values = [
            analytic_bulk_c1(config, field, partition)
            for _theta in CONTACT_ANGLES_DEG
        ]
        self.assertLessEqual(max(bulk_values) - min(bulk_values), BULK_INVARIANCE_TOLERANCE)
        interface_values = [
            analytic_interface_c1(config, field, partition, theta)
            for theta in CONTACT_ANGLES_DEG
        ]
        self.assertTrue(all(a <= b for a, b in zip(interface_values, interface_values[1:])))
        self.assertLess(interface_values[0], interface_values[-1])


if __name__ == "__main__":
    unittest.main()
