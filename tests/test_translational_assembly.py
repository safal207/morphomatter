from __future__ import annotations

import random
import unittest

from morphomatter.particle_anisotropy import PARTICLE_BY_NAME
from morphomatter.translational_assembly import (
    BETA_SCHEDULE,
    GRID_SIZE,
    PARTICLE_COUNT,
    SEEDS,
    SWEEPS_PER_BETA,
    LatticeState,
    _rotation_candidate,
    _translation_candidate,
    active_bonds,
    background_controls_hold,
    binding_score,
    random_state,
    run_anneal,
    spatial_metrics,
    validate_protocol,
)


class TranslationalAssemblyTests(unittest.TestCase):
    def test_protocol_constants_are_frozen(self) -> None:
        validate_protocol()
        self.assertEqual(GRID_SIZE, 6)
        self.assertEqual(PARTICLE_COUNT, 8)
        self.assertEqual(SEEDS, tuple(range(20001, 20033)))
        self.assertEqual(BETA_SCHEDULE, (0.0, 0.5, 1.0, 2.0, 4.0, 8.0))
        self.assertEqual(SWEEPS_PER_BETA, 300)

    def test_random_state_respects_excluded_volume_and_bounds(self) -> None:
        state = random_state(random.Random(12345))
        self.assertEqual(len(state.positions), PARTICLE_COUNT)
        self.assertEqual(len(set(state.positions)), PARTICLE_COUNT)
        self.assertTrue(all(0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE for x, y in state.positions))
        self.assertTrue(all(0 <= value < 4 for value in state.orientations))

    def test_duplicate_occupancy_is_rejected(self) -> None:
        positions = ((0, 0), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (0, 1))
        with self.assertRaises(ValueError):
            LatticeState(positions=positions, orientations=(0,) * PARTICLE_COUNT)

    def test_translation_wraps_and_respects_occupancy(self) -> None:
        state = LatticeState(
            positions=((5, 0), (2, 2), (3, 3), (4, 4), (1, 5), (0, 3), (3, 0), (5, 5)),
            orientations=(0,) * PARTICLE_COUNT,
        )
        moved = _translation_candidate(state, 0, "E")
        self.assertIsNotNone(moved)
        assert moved is not None
        self.assertEqual(moved.positions[0], (0, 0))

        blocked_state = LatticeState(
            positions=((5, 0), (0, 0), (3, 3), (4, 4), (1, 5), (0, 3), (3, 0), (5, 5)),
            orientations=(0,) * PARTICLE_COUNT,
        )
        self.assertIsNone(_translation_candidate(blocked_state, 0, "E"))

    def test_rotation_is_local_and_preserves_positions(self) -> None:
        state = LatticeState(
            positions=((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (0, 1), (1, 1)),
            orientations=(0, 1, 2, 3, 0, 1, 2, 3),
        )
        rotated = _rotation_candidate(state, 3, 1)
        self.assertEqual(rotated.positions, state.positions)
        self.assertEqual(rotated.orientations[3], 0)
        self.assertEqual(rotated.orientations[:3], state.orientations[:3])

    def test_axial_bond_uses_emergent_neighbor_contact(self) -> None:
        topology = PARTICLE_BY_NAME["axial2"]
        state = LatticeState(
            positions=((0, 0), (1, 0), (3, 0), (5, 0), (0, 2), (2, 2), (4, 2), (3, 4)),
            orientations=(0,) * PARTICLE_COUNT,
        )
        bonds = active_bonds(topology, state)
        # canonical axial2 ports are N/S at orientation 0, so the E/W contact
        # at (0,0)-(1,0) is geometrically present but directionally inactive.
        self.assertEqual(len(bonds), 0)
        self.assertEqual(binding_score(topology, state), 0.0)

        rotated = LatticeState(positions=state.positions, orientations=(1, 1, 0, 0, 0, 0, 0, 0))
        bonds = active_bonds(topology, rotated)
        self.assertEqual(len(bonds), 1)
        self.assertAlmostEqual(bonds[0].strength, 1.0, places=12)

    def test_metrics_remain_bounded(self) -> None:
        topology = PARTICLE_BY_NAME["tri3"]
        state = random_state(random.Random(7))
        metrics = spatial_metrics(topology, state)
        self.assertGreaterEqual(metrics.binding_utilization, 0.0)
        self.assertLessEqual(metrics.binding_utilization, 1.0)
        self.assertGreaterEqual(metrics.largest_component_fraction, 1.0 / PARTICLE_COUNT)
        self.assertLessEqual(metrics.largest_component_fraction, 1.0)
        self.assertTrue(all(
            0.0 <= value <= 1.0
            for value in (
                metrics.axial_fraction,
                metrics.corner_fraction,
                metrics.branch_fraction,
                metrics.cross_fraction,
            )
        ))

    def test_background_controls_hold(self) -> None:
        self.assertTrue(background_controls_hold())

    def test_same_seed_exactly_replays(self) -> None:
        first = run_anneal("corner2", 20001)
        second = run_anneal("corner2", 20001)
        self.assertEqual(first, second)
        self.assertEqual(first.proposals, len(BETA_SCHEDULE) * SWEEPS_PER_BETA * PARTICLE_COUNT)


if __name__ == "__main__":
    unittest.main()
