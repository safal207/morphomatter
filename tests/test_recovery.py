import unittest

from morphomatter import Conditions, Phase
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, compare_recovery_strategies, rectangular_sites


class RecoveryExperimentTests(unittest.TestCase):
    def _reference_and_damage(self):
        reference = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
        reference.run(
            [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
            + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
        )
        damage = apply_damage(
            reference.state,
            rectangular_sites(width=9, height=9, top=2, left=2, rows=4, cols=5),
        )
        return reference, damage

    def test_pinned_damage_removes_twenty_ordered_sites(self):
        reference, damage = self._reference_and_damage()
        self.assertEqual(sum(p is Phase.ORDERED for p in reference.state), 77)
        self.assertEqual(damage.ordered_sites_removed, 20)
        self.assertEqual(sum(p is Phase.ORDERED for p in damage.after), 57)

    def test_coupling_recovery_beats_no_coupling_and_bruteforce_efficiency(self):
        _, damage = self._reference_and_damage()
        renucleation = Conditions(drive=0.55, coupling_scale=1.0, threshold_scale=0.8)
        cooperative = [renucleation] * 2 + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 10
        no_coupling = [renucleation] * 2 + [Conditions(drive=0.12, coupling_scale=0.0, threshold_scale=0.8)] * 10
        brute = [Conditions(drive=0.80, coupling_scale=0.0, threshold_scale=0.8)] * 12

        results = compare_recovery_strategies(
            damage.after,
            config=NucleationConfig(width=9, height=9, seed=11),
            strategies={"cooperative": cooperative, "no_coupling": no_coupling, "brute": brute},
        )
        by_name = {result.name: result for result in results}

        self.assertEqual(by_name["cooperative"].final_ordered_fraction, 1.0)
        self.assertEqual(by_name["cooperative"].first_goal_tick, 5)
        self.assertAlmostEqual(by_name["no_coupling"].final_ordered_fraction, 73 / 81)
        self.assertAlmostEqual(by_name["brute"].final_ordered_fraction, 80 / 81)
        self.assertGreater(
            by_name["cooperative"].final_ordered_fraction,
            by_name["no_coupling"].final_ordered_fraction,
        )
        self.assertGreater(
            by_name["cooperative"].gain_per_effort,
            by_name["brute"].gain_per_effort,
        )
        self.assertTrue(all(result.replay_verified for result in results))

    def test_recovery_trace_contains_renucleation_and_frontier_growth(self):
        _, damage = self._reference_and_damage()
        schedule = (
            [Conditions(drive=0.55, coupling_scale=1.0, threshold_scale=0.8)] * 2
            + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 10
        )
        result = compare_recovery_strategies(
            damage.after,
            config=NucleationConfig(width=9, height=9, seed=11),
            strategies={"cooperative": schedule},
        )[0]
        mechanisms = dict(result.mechanism_counts)
        self.assertGreaterEqual(mechanisms.get("nucleation", 0), 1)
        self.assertGreaterEqual(mechanisms.get("frontier_growth", 0), 1)
        self.assertGreaterEqual(mechanisms.get("commit", 0), 1)


if __name__ == "__main__":
    unittest.main()
