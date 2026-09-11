from __future__ import annotations

import random
import unittest

from morphomatter.orientation_kinetics import (
    BETA_FAST,
    BETA_FAST_REVERSE,
    BETA_SLOW,
    FAST_SWEEPS_PER_BETA,
    MATCHED_PAIRS,
    RELAX_SWEEPS_AT_ZERO,
    SEEDS,
    SLOW_SWEEPS_PER_BETA,
    assignment_metrics,
    metropolis_proposal,
    run_fast_cycle,
    run_slow_anneal,
    validate_protocol,
)
from morphomatter.particle_anisotropy import MOTIF_BY_NAME, PARTICLE_BY_NAME


class OrientationKineticsTests(unittest.TestCase):
    def test_protocol_constants_are_frozen(self) -> None:
        validate_protocol()
        self.assertEqual(BETA_SLOW, (0.0, 0.5, 1.0, 2.0, 4.0, 8.0))
        self.assertEqual(BETA_FAST, (0.0, 0.5, 1.0, 2.0, 4.0, 8.0))
        self.assertEqual(BETA_FAST_REVERSE, (4.0, 2.0, 1.0, 0.5, 0.0))
        self.assertEqual(SLOW_SWEEPS_PER_BETA, 120)
        self.assertEqual(FAST_SWEEPS_PER_BETA, 2)
        self.assertEqual(RELAX_SWEEPS_AT_ZERO, 30)
        self.assertEqual(SEEDS, tuple(range(17001, 17033)))
        self.assertEqual(len(MATCHED_PAIRS), 4)

    def test_assignment_metrics_are_bounded(self) -> None:
        topology = PARTICLE_BY_NAME["corner2"]
        motif = MOTIF_BY_NAME["corner_loop4"]
        metrics = assignment_metrics(topology, motif, (0, 1, 2, 3))
        self.assertGreaterEqual(metrics.edge_coverage, 0.0)
        self.assertLessEqual(metrics.edge_coverage, 1.0)
        self.assertGreaterEqual(metrics.budget_utilization, 0.0)
        self.assertLessEqual(metrics.budget_utilization, 1.0)
        self.assertGreaterEqual(metrics.quality, 0.0)
        self.assertLessEqual(metrics.quality, 1.0)

    def test_beta_zero_accepts_downhill_proposals(self) -> None:
        topology = PARTICLE_BY_NAME["axial2"]
        motif = MOTIF_BY_NAME["axial_ring6"]
        state = (0, 0, 0, 0, 0, 0)
        rng = random.Random(19019)
        # At beta=0 every proposal is accepted, including any downhill move.
        for _ in range(20):
            new_state, accepted = metropolis_proposal(topology, motif, state, 0.0, rng)
            self.assertTrue(accepted)
            state = new_state

    def test_slow_anneal_is_deterministic_for_fixed_seed(self) -> None:
        first = run_slow_anneal("corner2", "corner_loop4", 17001)
        second = run_slow_anneal("corner2", "corner_loop4", 17001)
        self.assertEqual(first, second)

    def test_fast_cycle_is_deterministic_for_fixed_seed(self) -> None:
        first = run_fast_cycle("axial2", "axial_ring6", 17002)
        second = run_fast_cycle("axial2", "axial_ring6", 17002)
        self.assertEqual(first, second)

    def test_proposal_counts_match_frozen_protocol(self) -> None:
        slow = run_slow_anneal("axial2", "axial_ring6", 17003)
        motif = MOTIF_BY_NAME["axial_ring6"]
        self.assertEqual(
            slow.proposals,
            len(BETA_SLOW) * SLOW_SWEEPS_PER_BETA * motif.node_count,
        )

        cycle = run_fast_cycle("axial2", "axial_ring6", 17003)
        expected = (
            (len(BETA_FAST) + len(BETA_FAST_REVERSE)) * FAST_SWEEPS_PER_BETA
            + RELAX_SWEEPS_AT_ZERO
        ) * motif.node_count
        self.assertEqual(cycle.proposals, expected)

    def test_cycle_preserves_declared_beta_order(self) -> None:
        result = run_fast_cycle("tri3", "tri_ladder8", 17004)
        self.assertEqual(tuple(beta for beta, _ in result.forward_quality), BETA_FAST)
        self.assertEqual(tuple(beta for beta, _ in result.reverse_quality), BETA_FAST_REVERSE)


if __name__ == "__main__":
    unittest.main()
