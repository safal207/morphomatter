from __future__ import annotations

import unittest

from morphomatter.continuous_mpc import (
    COUPLING_BOUNDS,
    DRIVE_BOUNDS,
    THRESHOLD_BOUNDS,
    plan_next_conditions,
    run_continuous_mpc,
    validate_planner_protocol,
)
from morphomatter.core import Phase
from morphomatter.nucleation import NucleationConfig, NucleationLattice


class ContinuousMPCTests(unittest.TestCase):
    def test_protocol_is_frozen(self) -> None:
        validate_planner_protocol()
        self.assertEqual(DRIVE_BOUNDS, (0.02, 0.80))
        self.assertEqual(COUPLING_BOUNDS, (0.00, 1.80))
        self.assertEqual(THRESHOLD_BOUNDS, (0.70, 0.90))

    def test_planning_is_deterministic_and_does_not_mutate_state(self) -> None:
        initial = (Phase.ORDERED,) * 40 + (Phase.DISORDERED,) * 41
        model = NucleationLattice(
            initial,
            config=NucleationConfig(width=9, height=9, seed=149),
        )
        before_state = tuple(model.state)
        before_tick = model.tick

        left, _ = plan_next_conditions(
            model,
            remaining_ticks=9,
            goal_fraction=0.90,
            planner_seed=1_010_000,
        )
        right, _ = plan_next_conditions(
            model,
            remaining_ticks=9,
            goal_fraction=0.90,
            planner_seed=1_010_000,
        )

        self.assertEqual(left, right)
        self.assertEqual(tuple(model.state), before_state)
        self.assertEqual(model.tick, before_tick)
        self.assertGreaterEqual(left.drive, DRIVE_BOUNDS[0])
        self.assertLessEqual(left.drive, DRIVE_BOUNDS[1])
        self.assertGreaterEqual(left.coupling_scale, COUPLING_BOUNDS[0])
        self.assertLessEqual(left.coupling_scale, COUPLING_BOUNDS[1])
        self.assertGreaterEqual(left.threshold_scale, THRESHOLD_BOUNDS[0])
        self.assertLessEqual(left.threshold_scale, THRESHOLD_BOUNDS[1])

    def test_executed_schedule_stays_in_bounds_and_replays(self) -> None:
        initial = (Phase.ORDERED,) * 52 + (Phase.DISORDERED,) * 29
        result = run_continuous_mpc(
            initial,
            config=NucleationConfig(width=9, height=9, seed=151),
            lambda_index=0,
            case_index=0,
        )
        self.assertTrue(result.replay_verified)
        self.assertLessEqual(len(result.schedule), 9)
        for conditions in result.schedule:
            self.assertGreaterEqual(conditions.drive, DRIVE_BOUNDS[0])
            self.assertLessEqual(conditions.drive, DRIVE_BOUNDS[1])
            self.assertGreaterEqual(conditions.coupling_scale, COUPLING_BOUNDS[0])
            self.assertLessEqual(conditions.coupling_scale, COUPLING_BOUNDS[1])
            self.assertGreaterEqual(conditions.threshold_scale, THRESHOLD_BOUNDS[0])
            self.assertLessEqual(conditions.threshold_scale, THRESHOLD_BOUNDS[1])


if __name__ == "__main__":
    unittest.main()
