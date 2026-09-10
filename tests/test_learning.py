import unittest

from morphomatter import Conditions
from morphomatter.learning import TrainingCase, evaluate_learned_policy, train_tabular_policy
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, rectangular_sites


class LearnedRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assembly = (
            [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
            + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
        )
        reference_model = NucleationLattice(
            config=NucleationConfig(width=9, height=9, seed=26)
        )
        reference_model.run(assembly)
        cls.reference = tuple(reference_model.state)

        patterns = (
            rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=4),
            rectangular_sites(width=9, height=9, top=1, left=4, rows=4, cols=3),
            rectangular_sites(width=9, height=9, top=3, left=1, rows=3, cols=5),
            rectangular_sites(width=9, height=9, top=4, left=3, rows=3, cols=4),
        )
        cases = []
        for seed in (3, 7, 11, 19, 23):
            for pattern_index, sites in enumerate(patterns):
                cases.append(
                    TrainingCase(
                        name=f"rect-{pattern_index}-seed-{seed}",
                        initial_state=apply_damage(cls.reference, sites).after,
                        seed=seed,
                    )
                )
        cls.policy = train_tabular_policy(tuple(cases), episodes=1200, training_seed=2026)

    def test_held_out_damage_reaches_goal_with_low_effort(self):
        held_out_sites = rectangular_sites(
            width=9,
            height=9,
            top=2,
            left=2,
            rows=5,
            cols=5,
        )
        held_out = apply_damage(self.reference, held_out_sites)
        result = evaluate_learned_policy(
            self.policy,
            held_out.after,
            seed=37,
            max_steps=12,
            goal_fraction=0.90,
        )

        self.assertEqual(held_out.ordered_sites_removed, 25)
        self.assertIsNotNone(result.first_goal_tick)
        self.assertGreaterEqual(result.final_ordered_fraction, 0.90)
        self.assertLess(result.control_effort, 1.90)
        self.assertTrue(result.replay_verified)

    def test_training_is_reproducible_for_same_seed(self):
        small_cases = (
            TrainingCase(
                name="small",
                initial_state=apply_damage(
                    self.reference,
                    rectangular_sites(width=9, height=9, top=1, left=1, rows=3, cols=3),
                ).after,
                seed=7,
            ),
        )
        left = train_tabular_policy(small_cases, episodes=50, training_seed=99)
        right = train_tabular_policy(small_cases, episodes=50, training_seed=99)
        self.assertEqual(left.q_values, right.q_values)


if __name__ == "__main__":
    unittest.main()
