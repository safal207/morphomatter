import unittest

from morphomatter import Conditions, Phase
from morphomatter.nucleation import NucleationConfig, NucleationLattice


class NucleationLatticeTests(unittest.TestCase):
    def test_seeded_trajectory_is_reproducible(self):
        config = NucleationConfig(width=5, height=5, seed=11)
        schedule = [Conditions(drive=0.5, coupling_scale=1.2, threshold_scale=0.8)] * 8

        left = NucleationLattice(config=config)
        right = NucleationLattice(config=config)
        left.run(schedule)
        right.run(schedule)

        self.assertEqual(left.state, right.state)
        self.assertEqual(left.trace, right.trace)

    def test_nucleation_then_frontier_growth_reaches_mostly_ordered_state(self):
        config = NucleationConfig(width=9, height=9, seed=26)
        model = NucleationLattice(config=config)
        schedule = (
            [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
            + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
        )
        model.run(schedule)

        mechanisms = {event.mechanism for event in model.trace}
        self.assertIn("nucleation", mechanisms)
        self.assertIn("frontier_growth", mechanisms)
        self.assertIn("commit", mechanisms)
        self.assertGreaterEqual(model.ordered_fraction(), 0.90)

    def test_trace_replays_exactly(self):
        config = NucleationConfig(width=5, height=5, seed=3)
        model = NucleationLattice(config=config)
        model.run([Conditions(drive=0.55, coupling_scale=1.3, threshold_scale=0.8)] * 10)
        self.assertEqual(model.replay(), tuple(model.state))

    def test_zero_nucleation_probability_stays_disordered(self):
        config = NucleationConfig(
            width=4,
            height=4,
            seed=1,
            spontaneous_rate=0.0,
            nucleation_drive_gain=0.0,
            barrier=0.1,
        )
        model = NucleationLattice(config=config)
        model.run([Conditions(drive=0.0)] * 20)

        self.assertEqual(model.state, [Phase.DISORDERED] * 16)
        self.assertEqual(model.trace, [])


if __name__ == "__main__":
    unittest.main()
