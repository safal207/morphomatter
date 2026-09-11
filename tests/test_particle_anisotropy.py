from __future__ import annotations

import unittest

from morphomatter.particle_anisotropy import (
    CONTACT_MOTIFS,
    DIRECTIONAL_BUDGET,
    PARTICLE_TOPOLOGIES,
    ContactEdge,
    evaluate_assignment,
    exhaustive_optimum,
    validate_frozen_protocol,
)


class ParticleAnisotropyTests(unittest.TestCase):
    def test_frozen_protocol_validates(self) -> None:
        validate_frozen_protocol()

    def test_all_particle_families_have_equal_scalar_directional_budget(self) -> None:
        for topology in PARTICLE_TOPOLOGIES:
            self.assertAlmostEqual(topology.budget, DIRECTIONAL_BUDGET, places=12)
            for turns in range(4):
                self.assertAlmostEqual(
                    sum(topology.oriented_ports(turns)),
                    DIRECTIONAL_BUDGET,
                    places=12,
                )

    def test_all_motifs_have_declared_uniform_degree(self) -> None:
        expected = {
            "axial_ring6": 2,
            "corner_loop4": 2,
            "tri_ladder8": 3,
            "square_torus9": 4,
        }
        for motif in CONTACT_MOTIFS:
            motif.validate()
            self.assertEqual(set(motif.degrees()), {expected[motif.name]})

    def test_nonreciprocal_edge_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ContactEdge(0, 1, "N", "E")

    def test_assignment_utilization_is_bounded(self) -> None:
        # Technical spot checks only; scientific ranking is evaluated by the
        # preregistered Experiment 018 runner.
        for topology in PARTICLE_TOPOLOGIES:
            for motif in CONTACT_MOTIFS:
                orientations = tuple(0 for _ in range(motif.node_count))
                coverage, utilization, total = evaluate_assignment(
                    topology, motif, orientations
                )
                self.assertGreaterEqual(coverage, 0.0)
                self.assertLessEqual(coverage, 1.0)
                self.assertGreaterEqual(utilization, 0.0)
                self.assertLessEqual(utilization, 1.0)
                self.assertGreaterEqual(total, 0.0)

    def test_exhaustive_optimizer_evaluates_complete_small_space(self) -> None:
        topology = next(item for item in PARTICLE_TOPOLOGIES if item.name == "axial2")
        motif = next(item for item in CONTACT_MOTIFS if item.name == "corner_loop4")
        result = exhaustive_optimum(topology, motif)
        self.assertEqual(result.assignments_evaluated, 4 ** motif.node_count)
        self.assertGreaterEqual(result.optimal_assignment_count, 1)
        self.assertEqual(len(result.canonical_orientations), motif.node_count)


if __name__ == "__main__":
    unittest.main()
