import unittest

from morphomatter import Phase
from morphomatter.hard_learning import config_with_seed, train_policy_under_config
from morphomatter.learning import TrainingCase
from morphomatter.nucleation import NucleationConfig


class HardLearningTests(unittest.TestCase):
    def test_config_clone_changes_only_seed(self):
        base = NucleationConfig(
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
        changed = config_with_seed(base, 73)
        self.assertEqual(changed.seed, 73)
        self.assertEqual(changed.spontaneous_rate, base.spontaneous_rate)
        self.assertEqual(changed.nucleation_drive_gain, base.nucleation_drive_gain)
        self.assertEqual(changed.frontier_neighbor_gain, base.frontier_neighbor_gain)
        self.assertEqual(changed.barrier, base.barrier)

    def test_hard_training_is_deterministic(self):
        initial = tuple([Phase.ORDERED] * 60 + [Phase.DISORDERED] * 21)
        cases = (
            TrainingCase("a", initial, 5),
            TrainingCase("b", initial, 13),
        )
        config = NucleationConfig(width=9, height=9, seed=0, barrier=0.16)
        left = train_policy_under_config(
            cases,
            config_template=config,
            episodes=40,
            max_steps=3,
            goal_fraction=0.92,
            training_seed=6006,
        )
        right = train_policy_under_config(
            cases,
            config_template=config,
            episodes=40,
            max_steps=3,
            goal_fraction=0.92,
            training_seed=6006,
        )
        self.assertEqual(left.q_values, right.q_values)


if __name__ == "__main__":
    unittest.main()
