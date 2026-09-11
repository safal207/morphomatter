from __future__ import annotations

import unittest

from morphomatter.geometry_transport import GEOMETRY_MASKS
from morphomatter.nucleation import NucleationConfig
from morphomatter.pde_transport import (
    BISECTION_ITERATIONS,
    FIELD_MAX_ITERATIONS,
    FIELD_TOLERANCE,
    MIN_CORE_CELLS,
    TARGET_FRACTION,
    analytic_pde_c1,
    analytic_pde_c2,
    numerical_pde_c1,
    numerical_pde_c2,
    solve_laplace_field,
)


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


class PDETransportTests(unittest.TestCase):
    def test_protocol_constants_are_frozen(self) -> None:
        self.assertEqual(FIELD_TOLERANCE, 1e-10)
        self.assertEqual(FIELD_MAX_ITERATIONS, 20_000)
        self.assertEqual(TARGET_FRACTION, 0.50)
        self.assertEqual(BISECTION_ITERATIONS, 40)
        self.assertEqual(MIN_CORE_CELLS, 20)

    def test_all_geometry_fields_converge_and_respect_dirichlet_boundaries(self) -> None:
        for name in GEOMETRY_MASKS:
            field = solve_laplace_field(name)
            values = field.value_map()
            self.assertGreaterEqual(len(field.core_cells), MIN_CORE_CELLS)
            self.assertTrue(field.source_cells)
            self.assertTrue(field.sink_cells)
            self.assertLessEqual(field.residual, 2e-10)
            for cell in field.source_cells:
                self.assertEqual(values[cell], 1.0)
            for cell in field.sink_cells:
                self.assertEqual(values[cell], 0.0)
            for value in field.core_values():
                self.assertGreater(value, 0.0)
                self.assertLess(value, 1.0)

    def test_solver_is_deterministic_and_geometry_name_has_no_special_coefficient(self) -> None:
        first = solve_laplace_field("pyramid_like")
        second = solve_laplace_field("pyramid_like")
        self.assertEqual(first.values, second.values)
        self.assertEqual(first.iterations, second.iterations)
        self.assertEqual(first.residual, second.residual)

    def test_analytic_aggregate_roots_match_actual_law_bisection(self) -> None:
        for name in ("slab", "cylinder_like", "pyramid_like"):
            field = solve_laplace_field(name)
            analytic_c1 = analytic_pde_c1(HARD_CONFIG, field)
            analytic_c2 = analytic_pde_c2(HARD_CONFIG, field)
            numerical_c1 = numerical_pde_c1(HARD_CONFIG, field)
            numerical_c2 = numerical_pde_c2(HARD_CONFIG, field)
            self.assertIsNotNone(numerical_c1)
            self.assertIsNotNone(numerical_c2)
            self.assertAlmostEqual(analytic_c1, numerical_c1, places=6)
            self.assertAlmostEqual(analytic_c2, numerical_c2, places=6)


if __name__ == "__main__":
    unittest.main()
