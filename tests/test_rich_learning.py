import unittest

from morphomatter import Conditions, Phase
from morphomatter.learning import TrainingCase, state_key
from morphomatter.nucleation import (
    NucleationConfig,
    NucleationLattice,
    NucleationTransition,
)
from morphomatter.rich_learning import (
    rich_state_key,
    train_rich_policy_under_config,
)


class RichStateTests(unittest.TestCase):
    def test_rich_key_preserves_coarse_prefix_and_adds_components(self) -> None:
        state = (
            Phase.DISORDERED, Phase.ORDERED, Phase.ORDERED,
            Phase.ORDERED, Phase.ORDERED, Phase.ORDERED,
            Phase.ORDERED, Phase.ORDERED, Phase.DISORDERED,
        )
        model = NucleationLattice(
            state,
            config=NucleationConfig(width=3, height=3, seed=1),
        )
        rich = rich_state_key(model, max_steps=9)
        self.assertEqual(rich[:3], state_key(model))
        self.assertEqual(rich[4], 2)  # two disconnected non-ordered components
        self.assertEqual(len(rich), 8)

    def test_recent_commit_and_horizon_are_observed_without_case_labels(self) -> None:
        state = (Phase.METASTABLE,) + (Phase.ORDERED,) * 8
        model = NucleationLattice(
            state,
            config=NucleationConfig(width=3, height=3, seed=2),
        )
        before = rich_state_key(model, max_steps=9)
        model.tick = 1
        model.trace.append(
            NucleationTransition(
                tick=1,
                site=0,
                before=Phase.METASTABLE,
                after=Phase.ORDERED,
                mechanism="commit",
                probability=1.0,
                random_draw=0.0,
                ordered_neighbor_fraction=1.0,
                conditions=Conditions(drive=0.5, coupling_scale=1.0, threshold_scale=1.0),
            )
        )
        after = rich_state_key(model, max_steps=9)
        self.assertEqual(before[6], 0)
        self.assertEqual(after[6], 1)
        self.assertEqual(before[7], 2)
        self.assertEqual(after[7], 2)

    def test_training_is_deterministic_for_same_seed(self) -> None:
        initial = tuple(
            Phase.DISORDERED if 20 <= index < 35 else Phase.ORDERED
            for index in range(81)
        )
        cases = (
            TrainingCase(name="case-a", initial_state=initial, seed=3),
            TrainingCase(name="case-b", initial_state=initial, seed=7),
        )
        config = NucleationConfig(width=9, height=9, seed=0)
        left = train_rich_policy_under_config(
            cases,
            config_template=config,
            episodes=40,
            max_steps=5,
            training_seed=808,
        )
        right = train_rich_policy_under_config(
            cases,
            config_template=config,
            episodes=40,
            max_steps=5,
            training_seed=808,
        )
        self.assertEqual(left.q_values, right.q_values)
        self.assertEqual(left.action_order, right.action_order)


if __name__ == "__main__":
    unittest.main()
