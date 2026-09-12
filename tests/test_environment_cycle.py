"""Exp021 integrity tests: no scientific positive result is required to pass."""
from __future__ import annotations

from math import exp, isfinite
import random
import unittest

from morphomatter import environment_cycle as cycle
from morphomatter.particle_anisotropy import PARTICLE_BY_NAME, PARTICLE_TOPOLOGIES
from morphomatter.translational_assembly import (
    DIRECTIONS, GRID_SIZE, PARTICLE_COUNT, LatticeState,
    _rotation_candidate, _translation_candidate, binding_score, random_state,
)


def independent_energy(topology, state, coefficients):
    """All unordered particle pairs; no production contact or bond helpers."""
    total = 0.0
    cardinal = {(0, GRID_SIZE - 1): 0, (1, 0): 1,
                (0, 1): 2, (GRID_SIZE - 1, 0): 3}
    for i in range(PARTICLE_COUNT):
        xi, yi = state.positions[i]
        for j in range(i + 1, PARTICLE_COUNT):
            xj, yj = state.positions[j]
            index = cardinal.get(((xj - xi) % GRID_SIZE, (yj - yi) % GRID_SIZE))
            if index is None:
                continue
            pi = topology.canonical_ports[(index - state.orientations[i]) % 4]
            pj = topology.canonical_ports[(index + 2 - state.orientations[j]) % 4]
            total += coefficients[0] + coefficients[1] * min(pi, pj)
    return total


def isolated_contact(*, periodic=False, facing=False):
    positions = ((0, 0), (5 if periodic else 1, 0), (3, 1), (5, 2),
                 (1, 3), (3, 3), (5, 4), (2, 5))
    orientations = ((1, 1) if facing else (0, 0)) + (0,) * 6
    return LatticeState(positions, orientations)


class ScriptedRandom:
    """Deterministic proposal and acceptance draws, including blocked moves."""
    def __init__(self, choices, uniform=0.5):
        self.choices = iter(choices)
        self.uniform = uniform
        self.draws = 0

    def randrange(self, stop):
        value = next(self.choices)
        if not 0 <= value < stop:
            raise AssertionError("scripted draw outside support")
        return value

    def random(self):
        self.draws += 1
        return self.uniform


class EnvironmentCycleTests(unittest.TestCase):
    def test_frozen_protocol(self):
        cycle.validate_protocol()
        self.assertEqual(cycle.SEEDS, tuple(range(21001, 21017)))
        self.assertEqual(cycle.SWEEP_RATES, (32, 256))
        self.assertEqual(len(cycle.I_CYCLE), 13)
        self.assertEqual((cycle.WARMUP_SWEEPS, cycle.RELAXATION_SWEEPS), (256, 512))
        self.assertEqual((cycle.TOPOLOGY_NAME, cycle.Q_REL, cycle.BETA), ("axial2", 1.0, 8.0))

    def test_environment_coefficients_and_frozen_energy_control(self):
        previous = float("inf")
        for strength in cycle.I_UP:
            repulsion, attraction = cycle.energy_coefficients(strength)
            self.assertLess(repulsion, previous)
            self.assertEqual(attraction, -1.0)
            self.assertEqual(cycle.energy_coefficients(strength, coupled=False), (0.75, -1.0))
            previous = repulsion

    def test_nonfinite_environment_is_rejected_in_both_modes(self):
        for value in (float("nan"), float("inf"), -float("inf"), -1.0, 0.0):
            for coupled in (True, False):
                with self.subTest(value=value, coupled=coupled), self.assertRaises(ValueError):
                    cycle.energy_coefficients(value, coupled=coupled)

    def test_acceptance_rejects_nonfinite_values_and_negative_beta(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(ValueError):
                cycle.metropolis_acceptance(value)
            with self.assertRaises(ValueError):
                cycle.metropolis_acceptance(1.0, value)
        with self.assertRaises(ValueError):
            cycle.metropolis_acceptance(1.0, -1.0)
        self.assertEqual(cycle.metropolis_acceptance(100.0, 0.0), 1.0)
        self.assertEqual(cycle.metropolis_acceptance(-100.0), 1.0)

    def test_invalid_sweep_counts_and_schedules_are_rejected(self):
        for value in (-1, 0, 1.5, True, float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                cycle.run_cycle(123, value)
        for schedule in ((), (float("nan"),), (float("inf"),), (0.0,), (-1.0,)):
            with self.subTest(schedule=schedule), self.assertRaises(ValueError):
                cycle.run_cycle(123, 1, schedule=schedule)

    def test_repulsion_includes_incompatible_contacts(self):
        state = isolated_contact()
        topology = PARTICLE_BY_NAME["axial2"]
        self.assertEqual(len(cycle.occupied_contacts(state)), 1)
        self.assertEqual(binding_score(topology, state), 0.0)
        for strength in cycle.I_UP:
            coefficients = cycle.energy_coefficients(strength)
            self.assertAlmostEqual(cycle.contact_energy(topology, state, coefficients), coefficients[0])

    def test_facing_contact_can_change_energy_sign_with_environment(self):
        state = isolated_contact(facing=True)
        topology = PARTICLE_BY_NAME["axial2"]
        self.assertEqual(binding_score(topology, state), 1.0)
        self.assertGreater(cycle.contact_energy(topology, state, cycle.energy_coefficients(0.01)), 0.0)
        self.assertLess(cycle.contact_energy(topology, state, cycle.energy_coefficients(10.0)), 0.0)

    def test_periodic_contact_is_counted_once(self):
        state = isolated_contact(periodic=True, facing=True)
        self.assertEqual(len(cycle.occupied_contacts(state)), 1)
        topology = PARTICLE_BY_NAME["axial2"]
        coefficients = cycle.energy_coefficients(1.0)
        self.assertAlmostEqual(cycle.contact_energy(topology, state, coefficients), -0.25)
        self.assertAlmostEqual(independent_energy(topology, state, coefficients), -0.25)

    def test_global_energy_matches_independent_pair_oracle(self):
        rng = random.Random(21901)
        for topology in PARTICLE_TOPOLOGIES:
            for _ in range(12):
                state = random_state(rng)
                for strength in (0.01, 1.0, 10.0):
                    coefficients = cycle.energy_coefficients(strength)
                    self.assertAlmostEqual(cycle.contact_energy(topology, state, coefficients),
                                           independent_energy(topology, state, coefficients), places=11)

    def test_local_delta_matches_independent_global_delta(self):
        rng = random.Random(21902)
        for topology in PARTICLE_TOPOLOGIES:
            for _ in range(4):
                state = random_state(rng)
                for particle in range(PARTICLE_COUNT):
                    candidates = [_translation_candidate(state, particle, d) for d in DIRECTIONS]
                    candidates += [_rotation_candidate(state, particle, s) for s in (-1, 1)]
                    for candidate in candidates:
                        if candidate is None:
                            continue
                        for strength in (0.01, 1.0, 10.0):
                            coefficients = cycle.energy_coefficients(strength)
                            local_delta = (cycle.local_energy(topology, candidate, particle, coefficients)
                                           - cycle.local_energy(topology, state, particle, coefficients))
                            global_delta = (independent_energy(topology, candidate, coefficients)
                                            - independent_energy(topology, state, coefficients))
                            self.assertAlmostEqual(local_delta, global_delta, places=11)

    def test_fixed_environment_metropolis_detailed_balance(self):
        for beta in (0.0, 0.5, 8.0):
            for delta in (-3.0, -0.25, 0.0, 0.25, 3.0):
                forward = cycle.metropolis_acceptance(delta, beta)
                backward = cycle.metropolis_acceptance(-delta, beta)
                self.assertAlmostEqual(forward / backward / exp(-beta * delta), 1.0, places=12)

    def test_translation_and_rotation_proposals_have_inverse(self):
        rng = random.Random(21903)
        state = random_state(rng)
        reverse = {"N": "S", "E": "W", "S": "N", "W": "E"}
        for particle in range(PARTICLE_COUNT):
            for direction in DIRECTIONS:
                candidate = _translation_candidate(state, particle, direction)
                if candidate is not None:
                    self.assertEqual(_translation_candidate(candidate, particle, reverse[direction]), state)
            for step in (-1, 1):
                self.assertEqual(_rotation_candidate(_rotation_candidate(state, particle, step), particle, -step), state)

    def test_zero_repulsion_recovers_exp020_energy(self):
        state = random_state(random.Random(21904))
        for topology in PARTICLE_TOPOLOGIES:
            self.assertAlmostEqual(cycle.contact_energy(topology, state, (0.0, -1.0)),
                                   -binding_score(topology, state), places=12)

    def test_blocked_proposal_consumes_acceptance_draw(self):
        state = isolated_contact()
        rng = ScriptedRandom((0, 0, 1))  # particle 0 attempts east into particle 1
        result, accepted = cycle.proposal(PARTICLE_BY_NAME["axial2"], state, (0.75, -1.0), rng)
        self.assertEqual(result, state)
        self.assertFalse(accepted)
        self.assertEqual(rng.draws, 1)

    def test_energy_environment_changes_acceptance_not_proposals(self):
        state = isolated_contact(facing=True)
        topology = PARTICLE_BY_NAME["axial2"]
        low_rng = ScriptedRandom((0, 0, 3), 0.5)  # move west, breaking the facing contact
        high_rng = ScriptedRandom((0, 0, 3), 0.5)
        low_state, low_accepted = cycle.proposal(topology, state, cycle.energy_coefficients(0.01), low_rng)
        high_state, high_accepted = cycle.proposal(topology, state, cycle.energy_coefficients(10.0), high_rng)
        self.assertTrue(low_accepted)
        self.assertFalse(high_accepted)
        self.assertNotEqual(low_state, state)
        self.assertEqual(high_state, state)
        self.assertEqual((low_rng.draws, high_rng.draws), (1, 1))

    def test_exclusion_metrics_and_proposal_counts(self):
        result = cycle.run_cycle(21905, 2)
        self.assertEqual(len(result.stages), len(cycle.I_CYCLE))
        previous_accepted = 0
        for index, snapshot in enumerate(result.stages):
            self.assertEqual(snapshot.proposals, (cycle.WARMUP_SWEEPS + (index + 1) * 2) * PARTICLE_COUNT)
            self.assertEqual(len(set(snapshot.state.positions)), PARTICLE_COUNT)
            self.assertTrue(all(0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE for x, y in snapshot.state.positions))
            self.assertTrue(isfinite(snapshot.energy))
            self.assertTrue(0 <= snapshot.metrics.binding_utilization <= 1)
            self.assertTrue(previous_accepted <= snapshot.accepted <= snapshot.proposals)
            previous_accepted = snapshot.accepted
        self.assertEqual(result.relaxed.proposals,
                         (cycle.WARMUP_SWEEPS + len(cycle.I_CYCLE) * 2 + cycle.RELAXATION_SWEEPS) * PARTICLE_COUNT)

    def test_seeded_trace_replays_exactly(self):
        self.assertEqual(cycle.run_cycle(21906, 2), cycle.run_cycle(21906, 2))

    def test_uncoupled_external_labels_cannot_change_mechanical_trace(self):
        varied = cycle.run_cycle(21907, 2, coupled=False)
        constant = cycle.run_cycle(21907, 2, coupled=False, schedule=(1.0,) * len(cycle.I_CYCLE))
        self.assertEqual(varied.mechanical_trace(), constant.mechanical_trace())
        self.assertNotEqual(varied.stages[0].external_strength, constant.stages[0].external_strength)


if __name__ == "__main__":
    unittest.main()
