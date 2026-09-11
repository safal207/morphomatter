from __future__ import annotations

import unittest

from morphomatter.equal_flux_transport import (
    BISECTION_ITERATIONS,
    CONSERVATION_TOLERANCE,
    COUPLING_NUMERICAL_BOUNDS,
    DRIVE_NUMERICAL_BOUNDS,
    FIELD_MAX_ITERATIONS,
    FIELD_TOLERANCE,
    Q_TOTAL,
    TARGET_FRACTION,
    analytic_equal_flux_c1,
    analytic_equal_flux_c2,
    numerical_equal_flux_c1,
    numerical_equal_flux_c2,
    solve_equal_flux_field,
)
from morphomatter.geometry_transport import GEOMETRY_MASKS
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


class EqualFluxTransportTests(unittest.TestCase):
    def test_protocol_constants_are_frozen(self) -> None:
        self.assertEqual(Q_TOTAL, 1.0)
        self.assertEqual(FIELD_TOLERANCE, 1e-10)
        self.assertEqual(FIELD_MAX_ITERATIONS, 30_000)
        self.assertEqual(CONSERVATION_TOLERANCE, 1e-7)
        self.assertEqual(TARGET_FRACTION, 0.50)
        self.assertEqual(DRIVE_NUMERICAL_BOUNDS, (0.0, 50.0))
        self.assertEqual(COUPLING_NUMERICAL_BOUNDS, (0.0, 60.0))
        self.assertEqual(BISECTION_ITERATIONS, 50)

    def test_all_geometries_have_equal_total_flux_and_conserve_it(self) -> None:
        source_counts = {}
        for name in GEOMETRY_MASKS:
            field = solve_equal_flux_field(name)
            source_counts[name] = len(field.source_cells)
            self.assertAlmostEqual(field.total_injection, Q_TOTAL, places=12)
            self.assertAlmostEqual(
                field.injection_per_source * len(field.source_cells),
                Q_TOTAL,
                places=12,
            )
            self.assertLessEqual(
                abs(field.sink_flux - Q_TOTAL),
                CONSERVATION_TOLERANCE,
            )
            self.assertLessEqual(field.residual, 1e-8)
            values = field.value_map()
            for cell in field.sink_cells:
                self.assertEqual(values[cell], 0.0)
            for value in field.evaluation_values():
                self.assertGreater(value, 0.0)

        # The confound being controlled is total input, not aperture width.
        self.assertNotEqual(source_counts["slab"], source_counts["pyramid_like"])

    def test_solver_is_deterministic(self) -> None:
        first = solve_equal_flux_field("pyramid_like")
        second = solve_equal_flux_field("pyramid_like")
        self.assertEqual(first.values, second.values)
        self.assertEqual(first.iterations, second.iterations)
        self.assertEqual(first.residual, second.residual)
        self.assertEqual(first.sink_flux, second.sink_flux)

    def test_analytic_roots_match_actual_law_or_out_of_range_semantics(self) -> None:
        for name in GEOMETRY_MASKS:
            field = solve_equal_flux_field(name)
            analytic_c1 = analytic_equal_flux_c1(HARD_CONFIG, field)
            analytic_c2 = analytic_equal_flux_c2(HARD_CONFIG, field)
            numerical_c1 = numerical_equal_flux_c1(HARD_CONFIG, field)
            numerical_c2 = numerical_equal_flux_c2(HARD_CONFIG, field)

            if analytic_c1 > DRIVE_NUMERICAL_BOUNDS[1]:
                self.assertIsNone(numerical_c1)
            else:
                self.assertIsNotNone(numerical_c1)
                assert numerical_c1 is not None
                self.assertAlmostEqual(analytic_c1, numerical_c1, places=6)

            if analytic_c2 > COUPLING_NUMERICAL_BOUNDS[1]:
                self.assertIsNone(numerical_c2)
            else:
                self.assertIsNotNone(numerical_c2)
                assert numerical_c2 is not None
                self.assertAlmostEqual(analytic_c2, numerical_c2, places=6)


if __name__ == "__main__":
    unittest.main()
