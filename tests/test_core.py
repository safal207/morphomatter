import unittest

from morphomatter import Conditions, ModelConfig, PathGradientController, Phase, TransitionLattice


class TransitionLatticeTests(unittest.TestCase):
    def test_positive_conditions_cross_two_phase_boundaries(self):
        config = ModelConfig(width=2, height=2, transition_threshold=0.5, metastable_threshold=0.1, neighbor_coupling=0.0)
        model = TransitionLattice([Phase.DISORDERED] * 4, config=config)
        model.step(Conditions(drive=0.6))
        self.assertEqual(model.state, [Phase.METASTABLE] * 4)
        model.step(Conditions(drive=0.2))
        self.assertEqual(model.state, [Phase.ORDERED] * 4)

    def test_trace_replays_exactly(self):
        config = ModelConfig(width=2, height=2, neighbor_coupling=0.0)
        model = TransitionLattice([Phase.DISORDERED] * 4, config=config)
        model.step(Conditions(drive=0.8))
        model.step(Conditions(drive=0.3))
        self.assertEqual(model.replay(), tuple(model.state))

    def test_neighbor_coupling_can_push_metastable_site_forward(self):
        config = ModelConfig(width=3, height=1, transition_threshold=0.8, metastable_threshold=0.1, neighbor_coupling=0.8)
        model = TransitionLattice([Phase.ORDERED, Phase.METASTABLE, Phase.ORDERED], config=config)
        model.step(Conditions(drive=0.0))
        self.assertEqual(model.state[1], Phase.ORDERED)

    def test_path_gradient_controller_is_a_baseline_not_ai(self):
        config = ModelConfig(width=2, height=2, neighbor_coupling=0.0)
        model = TransitionLattice([Phase.DISORDERED] * 4, config=config)
        controller = PathGradientController(base_drive=0.6, boost=0.2)
        first = controller.choose(model)
        model.step(first)
        second = controller.choose(model)
        self.assertEqual(second.drive, 0.6)
        model.step(Conditions(drive=0.0))
        third = controller.choose(model)
        self.assertEqual(third.drive, 0.8)


if __name__ == "__main__":
    unittest.main()
