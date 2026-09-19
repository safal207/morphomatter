"""063B: fresh correctness checks, not external independent review."""
from dataclasses import replace
import inspect
import random
import unittest

from morphomatter.exp063 import (
    BudgetLedger, Candidate, EvidenceStore, Observation, POLICIES as LEGACY_POLICIES,
    Scenario, Task, World, branches, group_risk, make_world, run_policy,
)
from morphomatter.exp063b import (
    POLICIES, PairScorer, accept_receipt, feasible_candidates, make_scoped_world,
    run_guarded, scope_world, unavailable, validate_scenario,
)

PRIOR = (1 / 16,) * 16


def probe(name="a", kind="replication", bit=0, cost=1, source=None,
          accuracy=1.0, nulls=(0.0, 0.0, 0.0)):
    return Candidate(name, 0, kind, bit, source or name, "scope", cost, accuracy, nulls)


def fixture(candidates, tasks=None, prior=PRIOR):
    return Scenario((prior,), tuple(tasks or [Task("t", 0, (0,), "all", 1)]), tuple(candidates))


def receipt(c, outcome="ZERO"):
    return Observation("record:" + c.source_id, c.experiment_id, c.source_id, c.scope, outcome)


class PairLookaheadTests(unittest.TestCase):
    def test_01_exact_xor_pair_is_useful_when_singles_are_not(self):
        a = probe("audit", "audit")
        s = probe("sensor", "sensor")
        sc = fixture([s, a])
        scorer = PairScorer(sc)
        chosen, plans, reason = scorer.choose((PRIOR,), set(), 2, 2)
        self.assertEqual(chosen.experiment_id, "audit")
        self.assertEqual(plans[0]["plan"], ["audit", "sensor"])
        self.assertAlmostEqual(plans[0]["gain"], 1.0)
        self.assertAlmostEqual(plans[0]["score"], 0.5)
        self.assertTrue(all(abs(p["gain"]) < 1e-12 for p in plans if len(p["plan"]) == 1))

    def test_02_xor_pair_executes_and_succeeds_for_all_latent_states(self):
        sc = fixture([probe("audit", "audit"), probe("sensor", "sensor")])
        for latent in range(16):
            with self.subTest(latent=latent):
                world = World(sc, (latent,), 0)
                greedy = run_guarded(world, "decision_value", 2, 2)
                pair = run_guarded(world, "pair_value", 2, 2)
                self.assertEqual((greedy["spent"], greedy["hold"]), (0, 1))
                self.assertEqual((pair["spent"], pair["correct"], pair["loss"]), (2, 1, 0.0))

    def test_03_joint_score_matches_full_outcome_posterior_enumeration(self):
        cases = [
            (probe("s", "sensor", accuracy=0.81, nulls=(0.03, 0.03, 0.02)),
             probe("a", "audit", accuracy=0.9, nulls=(0.1, 0.0, 0.02))),
            (probe("r0", bit=0, accuracy=0.7), probe("r1", bit=1, accuracy=0.93)),
            (probe("s0", "sensor", bit=0, accuracy=0.97),
             probe("s1", "sensor", bit=1, accuracy=0.97)),
            (probe("n", "null", accuracy=0.5), probe("r", accuracy=0.86)),
        ]
        priors = [PRIOR, tuple((0.2 if h & 8 else 0.8) / 8 for h in range(16))]
        tasks = [Task("t0", 0, (0,), "all", 1), Task("t1", 0, (0, 1), "all", 3),
                 Task("t2", 0, (1, 2), "any", 1)]
        for a, b in cases:
            for prior in priors:
                sc = fixture([a, b], tasks, prior)
                expected = sum(p1 * p2 * group_risk(sc, 0, p_after2)
                               for _, p1, p_after1 in branches(prior, a)
                               for _, p2, p_after2 in branches(p_after1, b))
                scorer = PairScorer(sc)
                self.assertAlmostEqual(scorer.expected_risk(prior, a, b), expected, places=11)
                self.assertAlmostEqual(scorer.expected_risk(prior, b, a), expected, places=11)

    def test_04_aliases_never_form_an_independent_pair(self):
        a = probe("a", "sensor")
        alias = replace(a, experiment_id="copy")
        sc = fixture([a, alias])
        scorer = PairScorer(sc)
        _, plans, _ = scorer.choose((PRIOR,), set(), 4, 2)
        self.assertEqual(len(plans), 1)
        with self.assertRaises(ValueError):
            scorer.expected_risk(PRIOR, a, alias)

    def test_05_joint_plan_cannot_exceed_budget(self):
        sc = fixture([probe("audit", "audit"), probe("sensor", "sensor")])
        selected, plans, _ = PairScorer(sc).choose((PRIOR,), set(), 1, 2)
        self.assertIsNone(selected)
        self.assertTrue(all(p["planned_cost"] <= 1 for p in plans))

    def test_06_joint_plan_cannot_exceed_remaining_steps(self):
        sc = fixture([probe("audit", "audit"), probe("sensor", "sensor")])
        selected, plans, _ = PairScorer(sc).choose((PRIOR,), set(), 2, 1)
        self.assertIsNone(selected)
        self.assertTrue(all(len(p["plan"]) == 1 for p in plans))

    def test_07_cheap_perfect_singleton_dominates_expensive_pairs(self):
        sc = fixture([probe("direct"), probe("audit", "audit", cost=2), probe("sensor", "sensor")])
        chosen, plans, _ = PairScorer(sc).choose((PRIOR,), set(), 4, 2)
        self.assertEqual(chosen.experiment_id, "direct")
        self.assertEqual(plans[0]["plan"], ["direct"])
        self.assertAlmostEqual(plans[0]["score"], 1.0)

    def test_08_no_spurious_gain_from_two_uninformative_probes(self):
        sc = fixture([probe("n0", "null"), probe("n1", "null")])
        chosen, plans, _ = PairScorer(sc).choose((PRIOR,), set(), 4, 2)
        self.assertIsNone(chosen)
        self.assertTrue(all(p["gain"] <= 1e-12 for p in plans))

    def test_09_independent_groups_have_additive_gain(self):
        a, b = probe("a"), replace(probe("b"), group=1)
        sc = Scenario((PRIOR, PRIOR), (Task("t0", 0, (0,), "all", 1),
                                      Task("t1", 1, (0,), "all", 3)), (a, b))
        _, plans, _ = PairScorer(sc).choose(sc.priors, set(), 2, 2)
        pair = next(p for p in plans if len(p["plan"]) == 2)
        self.assertAlmostEqual(pair["gain"], 4.0)
        self.assertAlmostEqual(pair["score"], 2.0)

    def test_10_candidate_order_does_not_change_selected_plan(self):
        a, s = probe("audit", "audit"), probe("sensor", "sensor")
        for order in ([a, s], [s, a]):
            _, plans, _ = PairScorer(fixture(order)).choose((PRIOR,), set(), 2, 2)
            self.assertEqual(plans[0]["plan"], ["audit", "sensor"])


class ReviewRegressionTests(unittest.TestCase):
    def test_11_reproduce_valid_but_wrong_dispatch_receipt_in_v1(self):
        cheap, expensive = probe("a", cost=1), probe("b", cost=4)
        sc = fixture([cheap, expensive])
        class SubstitutionWorld(World):
            def observe(self, selected):
                return receipt(expensive, "ONE")
        world = SubstitutionWorld(sc, (0,), 0)
        legacy = run_policy(world, "decision_value", 1)
        guarded = run_guarded(world, "decision_value", 1)
        # Original verifier accepts a valid contract for an experiment never purchased.
        self.assertEqual((legacy["wrong"], legacy["spent"]), (1, 1))
        self.assertEqual((guarded["wrong"], guarded["hold"], guarded["spent"]), (0, 1, 1))
        self.assertEqual(guarded["receipt_rejections"], 1)
        self.assertEqual(guarded["known_invalid_leakage"], 0)

    def test_12_rejected_receipt_does_not_destroy_independent_evidence(self):
        a, b = probe("a"), probe("b", bit=1)
        store = EvidenceStore(fixture([a, b]))
        store.ingest(receipt(b, "ZERO"))
        before = store.posterior()
        self.assertEqual(accept_receipt(store, a, receipt(b, "ONE")), "RECEIPT_DISPATCH_MISMATCH")
        self.assertEqual(store.posterior(), before)
        self.assertIn(b.source_id, store.valid)

    def test_13_world_scope_rejects_receipt_from_another_world(self):
        first, second = make_scoped_world(200), make_scoped_world(201)
        a = first.scenario.candidates[0]
        b = next(c for c in second.scenario.candidates if c.experiment_id == a.experiment_id)
        self.assertEqual(a.source_id, b.source_id)
        self.assertNotEqual(a.scope, b.scope)
        store = EvidenceStore(replace(second.scenario, initial=()))
        self.assertEqual(accept_receipt(store, b, first.observe(a)), "RECEIPT_DISPATCH_MISMATCH")
        self.assertFalse(store.valid)

    def test_14_original_scope_contract_is_not_cross_world_identity(self):
        first, second = make_world(200), make_world(201)
        a = first.scenario.candidates[0]
        b = next(c for c in second.scenario.candidates if c.experiment_id == a.experiment_id)
        self.assertEqual(a.scope, b.scope)
        store = EvidenceStore(replace(second.scenario, initial=()))
        self.assertEqual(store.ingest(receipt(a)), "VALID")

    def test_15_unseen_invalidated_source_cannot_be_selected(self):
        c = probe()
        sc = fixture([c])
        store, ledger = EvidenceStore(sc), BudgetLedger(2)
        store.invalidate(c.source_id)
        self.assertNotIn(c.source_id, store.attempted)
        self.assertIn(c.source_id, unavailable(store, ledger))
        self.assertEqual(feasible_candidates(sc, unavailable(store, ledger), 2), ())

    def test_16_strict_bit_type_prevents_float_shift_and_bool_alias(self):
        for value in (True, 1.0):
            with self.subTest(value=value):
                candidate = replace(probe(), bit=value)  # Accepted by archived contract.
                with self.assertRaises(ValueError):
                    validate_scenario(fixture([candidate]))

    def test_17_legacy_clean_endpoints_unchanged_under_shared_guards(self):
        endpoints = ("loss", "correct", "wrong", "hold", "spent", "steps")
        for seed in (200, 201, 202):
            for policy in LEGACY_POLICIES:
                with self.subTest(seed=seed, policy=policy):
                    original = run_policy(make_world(seed), policy)
                    guarded = run_guarded(make_scoped_world(seed), policy)
                    self.assertEqual({k: original[k] for k in endpoints}, {k: guarded[k] for k in endpoints})

    def test_18_full_records_replay_for_all_policies(self):
        for policy in POLICIES:
            with self.subTest(policy=policy):
                a = run_guarded(make_scoped_world(200), policy)
                b = run_guarded(make_scoped_world(200), policy)
                self.assertEqual(a, b)
                self.assertTrue(a["ledger_chain_valid"])
                self.assertEqual(a["budget_violation"], 0)

    def test_19_selector_has_no_evaluator_truth_or_world_argument(self):
        self.assertNotIn("world", inspect.signature(PairScorer.choose).parameters)
        self.assertNotIn("hidden", inspect.signature(PairScorer.choose).parameters)
        sc = fixture([probe("audit", "audit"), probe("sensor", "sensor")])
        first = run_guarded(World(sc, (0,), 7), "pair_value", 2)["ledger"][0]
        other = run_guarded(World(sc, (15,), 7), "pair_value", 2)["ledger"][0]
        self.assertEqual(first, other)

    def test_20_step_limit_is_reported_as_step_limit(self):
        sc = fixture([probe("a"), probe("b", bit=1)])
        result = run_guarded(World(sc, (0,), 0), "cheapest", budget=10, maximum_steps=1)
        self.assertEqual(result["stop_reason"], "STEP_LIMIT")
        self.assertEqual(result["steps"], 1)

    def test_21_null_outcome_charged_without_repeat(self):
        c = probe()
        sc = fixture([c])
        class UnknownWorld(World):
            def observe(self, selected):
                return receipt(selected, "EXECUTION_UNKNOWN")
        result = run_guarded(UnknownWorld(sc, (0,), 0), "pair_value", 3)
        self.assertEqual((result["spent"], result["steps"], result["hold"]), (1, 1, 1))

    def test_22_scope_wrapper_preserves_preexisting_mismatch(self):
        c = probe()
        bad = replace(receipt(c), scope="wrong-history")
        world = scope_world(World(replace(fixture([c]), initial=(bad,)), (0,), 0))
        store = EvidenceStore(world.scenario)
        self.assertEqual(store.events[0]["status"], "SCOPE_MISMATCH")


if __name__ == "__main__":
    unittest.main()
