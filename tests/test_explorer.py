import unittest

from morphomatter import Conditions, ModelConfig, Phase, TransitionLattice
from morphomatter.explorer import TransitionMapExplorer, condition_grid


class TransitionMapExplorerTests(unittest.TestCase):
    def test_scan_separates_no_transition_from_ordering_region(self):
        config = ModelConfig(
            width=1,
            height=1,
            transition_threshold=0.5,
            metastable_threshold=0.1,
            neighbor_coupling=0.0,
        )
        explorer = TransitionMapExplorer(config, steps_per_point=2)
        records = explorer.scan(
            [Phase.DISORDERED],
            condition_grid((0.0, 0.6)),
        )

        self.assertEqual(records[0].dominant_phase, Phase.DISORDERED)
        self.assertEqual(records[0].organization_score, 0.0)
        self.assertEqual(records[1].dominant_phase, Phase.ORDERED)
        self.assertEqual(records[1].organization_score, 1.0)

    def test_schedule_search_finds_two_boundary_crossings(self):
        config = ModelConfig(
            width=1,
            height=1,
            transition_threshold=0.5,
            metastable_threshold=0.1,
            neighbor_coupling=0.0,
        )
        explorer = TransitionMapExplorer(config)
        result = explorer.find_schedule(
            [Phase.DISORDERED],
            condition_grid((0.0, 0.3, 0.6)),
            max_steps=2,
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(tuple(c.drive for c in result.schedule), (0.6, 0.3))
        self.assertEqual(result.final_state, (Phase.ORDERED,))

        replay_model = TransitionLattice([Phase.DISORDERED], config=config)
        for conditions in result.schedule:
            replay_model.step(conditions)
        self.assertEqual(replay_model.replay(), tuple(replay_model.state))
        self.assertEqual(tuple(replay_model.state), result.final_state)

    def test_schedule_search_refuses_hidden_memory_state(self):
        config = ModelConfig(width=1, height=1, memory_decay=0.5)
        explorer = TransitionMapExplorer(config)
        with self.assertRaisesRegex(ValueError, "memory_decay == 0"):
            explorer.find_schedule(
                [Phase.DISORDERED],
                [Conditions(drive=1.0)],
            )


if __name__ == "__main__":
    unittest.main()
