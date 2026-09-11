import unittest

from morphomatter.action_space import (
    EXPANDED_RECOVERY_ACTIONS,
    EXTRA_RECOVERY_ACTIONS,
    validate_expanded_action_space,
)
from morphomatter.learning import RECOVERY_ACTIONS


class ExpandedActionSpaceTests(unittest.TestCase):
    def test_original_actions_are_exact_prefix(self) -> None:
        self.assertEqual(
            tuple(EXPANDED_RECOVERY_ACTIONS)[: len(RECOVERY_ACTIONS)],
            tuple(RECOVERY_ACTIONS),
        )
        for name, conditions in RECOVERY_ACTIONS.items():
            self.assertEqual(EXPANDED_RECOVERY_ACTIONS[name], conditions)

    def test_expanded_action_space_is_frozen_at_eleven(self) -> None:
        validate_expanded_action_space()
        self.assertEqual(len(RECOVERY_ACTIONS), 5)
        self.assertEqual(len(EXTRA_RECOVERY_ACTIONS), 6)
        self.assertEqual(len(EXPANDED_RECOVERY_ACTIONS), 11)

    def test_extra_actions_remain_global_condition_triplets(self) -> None:
        expected = {
            "couple_gentle": (0.08, 1.80, 0.80),
            "couple_strong": (0.18, 1.80, 0.80),
            "bridge_drive": (0.38, 1.20, 0.80),
            "cooperate_low_threshold": (0.12, 1.50, 0.70),
            "renucleate_low_threshold": (0.55, 1.00, 0.70),
            "stabilize_high_threshold": (0.08, 1.50, 0.90),
        }
        observed = {
            name: (
                conditions.drive,
                conditions.coupling_scale,
                conditions.threshold_scale,
            )
            for name, conditions in EXTRA_RECOVERY_ACTIONS.items()
        }
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
