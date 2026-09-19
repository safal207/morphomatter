"""Correctness tests, not acceptance tests that force a scheduler victory."""
from dataclasses import replace
import inspect
import math
import random
import unittest

from experiments.exp063 import bootstrap, validate_lock
from morphomatter.exp063 import (
    BudgetLedger, Candidate, EvidenceStore, Observation, OUTCOMES, POLICIES,
    Scenario, Task, World, branches, candidate_score, check_chain, conditioned,
    digest, group_risk, invalid_source_uses, load_manifest, make_world, run_policy, select,
)

PRIOR = tuple(1 / 16 for _ in range(16))


def probe(name="rep", kind="replication", bit=0, cost=1, source="source"):
    return Candidate(name, 0, kind, bit, source, "scope-v1", cost, 1.0, (0.0, 0.0, 0.0))


def tiny(candidates=None, tasks=None):
    return Scenario((PRIOR,), tuple(tasks or [Task("task", 0, (0,), "all", 1)]),
                    tuple(candidates or [probe()]))


def observation(candidate, value="ZERO", record="record"):
    return Observation(record, candidate.experiment_id, candidate.source_id, candidate.scope, value)


class Exp063Tests(unittest.TestCase):
    def test_01_exact_one_step_value_against_enumeration(self):
        sc = tiny()
        candidate = sc.candidates[0]
        # All 16 equally likely states: before = HOLD loss 1; after exact bit measurement = 0.
        self.assertEqual(group_risk(sc, 0, PRIOR), 1.0)
        enumerated = 0.0
        for result in ("ZERO", "ONE"):
            hypotheses = [h for h in range(16) if candidate.likelihood(h, result) == 1]
            post = tuple(1 / len(hypotheses) if h in hypotheses else 0 for h in range(16))
            enumerated += len(hypotheses) / 16 * group_risk(sc, 0, post)
        self.assertEqual(enumerated, 0.0)
        self.assertAlmostEqual(candidate_score(sc, (PRIOR,), candidate, "decision_value"), 1.0)

    def test_02_null_probe_has_no_information_or_decision_value(self):
        c = probe(kind="null")
        sc = tiny([c])
        for policy in ("information_gain", "decision_value"):
            self.assertAlmostEqual(candidate_score(sc, (PRIOR,), c, policy), 0.0)

    def test_03_audit_can_be_informative_without_immediate_decision_value(self):
        c = probe(kind="audit")
        sc = tiny([c])
        self.assertAlmostEqual(candidate_score(sc, (PRIOR,), c, "information_gain"), 1.0)
        self.assertAlmostEqual(candidate_score(sc, (PRIOR,), c, "decision_value"), 0.0)

    def test_04_complementary_pair_exposes_greedy_stop(self):
        sensor = probe("sensor", "sensor", source="s")
        audit = probe("audit", "audit", source="a")
        sc = tiny([sensor, audit])
        selected, _, reason = select(sc, (PRIOR,), set(), 2, "decision_value", random.Random(0))
        self.assertIsNone(selected)
        self.assertEqual(reason, "NO_POSITIVE_EXPECTED_VALUE_UNDER_CURRENT_MODEL")
        joint_risk = sum(p * p2 * group_risk(sc, 0, after2)
                         for _, p, after in branches(PRIOR, sensor)
                         for _, p2, after2 in branches(after, audit))
        self.assertAlmostEqual(joint_risk, 0.0)

    def test_05_duplicate_evidence_does_not_change_posterior(self):
        sc = tiny()
        store = EvidenceStore(sc)
        c = sc.candidates[0]
        self.assertEqual(store.ingest(observation(c)), "VALID")
        before = store.posterior()
        for k in range(20):
            self.assertEqual(store.ingest(observation(c, record=f"clone{k}")), "DUPLICATE_SOURCE")
        self.assertEqual(store.posterior(), before)
        self.assertEqual(len(store.valid), 1)

    def test_06_alias_deduplication_before_selection(self):
        c = probe()
        sc = tiny([c, replace(c, experiment_id="alias")])
        _, scores, _ = select(sc, (PRIOR,), set(), 2, "decision_value", random.Random(0))
        self.assertEqual(len(scores), 1)

    def test_07_conflicting_same_source_is_quarantined(self):
        c = probe()
        store = EvidenceStore(tiny([c]))
        store.ingest(observation(c, "ZERO"))
        self.assertEqual(store.ingest(observation(c, "ONE", "contradiction")), "SOURCE_CONFLICT")
        self.assertEqual(store.posterior(), (PRIOR,))
        self.assertEqual(store.ingest(observation(c)), "SOURCE_QUARANTINED")

    def test_08_scope_mismatch_is_rejected(self):
        c = probe()
        store = EvidenceStore(tiny([c]))
        self.assertEqual(store.ingest(replace(observation(c), scope="other-history")), "SCOPE_MISMATCH")
        self.assertEqual(store.posterior(), (PRIOR,))

    def test_09_source_binding_is_verified(self):
        c = probe()
        store = EvidenceStore(tiny([c]))
        self.assertEqual(store.ingest(replace(observation(c), source_id="invented")), "SOURCE_BINDING_MISMATCH")
        self.assertFalse(store.valid)

    def test_10_stale_source_removed_independent_evidence_preserved(self):
        c = probe("first", source="first")
        other = probe("second", bit=1, source="second")
        sc = tiny([c, other])
        store = EvidenceStore(sc)
        store.ingest(observation(c))
        store.ingest(observation(other, "ONE", "second"))
        store.invalidate(c.source_id)
        expected = conditioned(PRIOR, other, "ONE")
        self.assertEqual(store.posterior(), (expected,))
        self.assertEqual(set(store.valid), {other.source_id})

    def test_11_invalid_costs_fail_closed(self):
        for cost in (0, -1, True, 1.5, float("nan"), float("inf")):
            with self.subTest(cost=cost), self.assertRaises(ValueError):
                probe(cost=cost)

    def test_12_duplicate_task_id_is_not_extra_benefit(self):
        task = Task("one", 0, (0,), "all", 1)
        with self.assertRaises(ValueError):
            tiny(tasks=[task, task])

    def test_13_invalid_alias_contract_is_rejected(self):
        c = probe()
        with self.assertRaises(ValueError):
            tiny([c, replace(c, experiment_id="alias", bit=1)])

    def test_14_null_outcomes_consume_cost_and_never_auto_retry(self):
        c = replace(probe(cost=2), null_probabilities=(0.03, 0.03, 0.02))
        for value in ("INCONCLUSIVE", "FAILED", "EXECUTION_UNKNOWN"):
            class FailureWorld(World):
                def observe(self, candidate):
                    return observation(candidate, value)
            with self.subTest(outcome=value):
                row = run_policy(FailureWorld(tiny([c]), (0,), 0), "decision_value", 4)
                self.assertEqual(row["spent"], 2)
                self.assertEqual(row["steps"], 1)
                self.assertEqual(row["hold"], 1)
                self.assertEqual(row["wrong"], 0)
                self.assertEqual(row["ledger"][1]["payload"]["verification_status"], value)

    def test_15_budget_reservation_rejects_duplicate_and_overspend(self):
        ledger = BudgetLedger(1)
        c = probe()
        ledger.reserve(c, {})
        with self.assertRaises(ValueError):
            ledger.reserve(c, {})
        with self.assertRaises(ValueError):
            ledger.reserve(probe("different", source="different"), {})
        self.assertEqual(ledger.remaining, 0)

    def test_16_outcome_probabilities_and_posteriors_normalize(self):
        world = make_world(0)
        for c in world.scenario.candidates:
            for h in range(16):
                self.assertAlmostEqual(sum(c.likelihood(h, o) for o in OUTCOMES), 1.0)
            options = branches(PRIOR, c)
            self.assertAlmostEqual(sum(p for _, p, _ in options), 1.0)
            for _, _, post in options:
                self.assertAlmostEqual(sum(post), 1.0)

    def test_17_selector_does_not_receive_evaluator_truth(self):
        self.assertNotIn("world", inspect.signature(select).parameters)
        self.assertNotIn("hidden", inspect.signature(select).parameters)
        sc = tiny()
        a = run_policy(World(sc, (0,), 5), "decision_value", 1)
        b = run_policy(World(sc, (15,), 5), "decision_value", 1)
        self.assertEqual(a["ledger"][0], b["ledger"][0])

    def test_18_full_trace_replays_for_every_policy(self):
        for policy in POLICIES:
            with self.subTest(policy=policy):
                self.assertEqual(run_policy(make_world(4), policy), run_policy(make_world(4), policy))

    def test_19_manifest_fixture_dimensions(self):
        world = make_world(10)
        self.assertEqual(len(world.scenario.priors) * 3, 12)
        self.assertEqual(len(world.scenario.tasks), 24)
        self.assertEqual(len(world.scenario.candidates), 36)
        self.assertEqual(set(t.weight for t in world.scenario.tasks), {1, 3})

    def test_20_all_hold_is_honest_baseline(self):
        world = make_world(4)
        row = run_policy(world, "hold")
        self.assertEqual(row["spent"], 0)
        self.assertEqual(row["hold"], 24)
        self.assertEqual(row["loss"], sum(t.weight for t in world.scenario.tasks))

    def test_21_small_matrix_integrity(self):
        for seed in (0, 3, 7):
            for policy in POLICIES:
                row = run_policy(make_world(seed), policy)
                self.assertLessEqual(row["spent"], 12)
                self.assertEqual(row["known_invalid_leakage"], 0)
                self.assertEqual(row["budget_violation"], 0)
                self.assertTrue(row["ledger_chain_valid"])
                self.assertEqual(row["correct"] + row["wrong"] + row["hold"], 24)

    def test_22_hash_chain_detects_modification(self):
        ledger = BudgetLedger(2)
        ledger.reserve(probe(), {"expected": 1})
        self.assertTrue(check_chain(ledger.events))
        ledger.events[0]["payload"]["budget_after"] = 200
        self.assertFalse(check_chain(ledger.events))

    def test_23_invalid_source_metric_is_not_hardcoded_zero(self):
        store = EvidenceStore(tiny())
        decisions = [{"action": "TRUE", "evidence_sources": ["missing"]}]
        self.assertEqual(invalid_source_uses(decisions, store), 1)

    def test_24_shared_audit_changes_multiple_claims(self):
        world = make_world(0)
        sc = replace(world.scenario, initial=())
        store = EvidenceStore(sc)
        for c in sc.candidates:
            if c.group == 0 and c.experiment_id == f"g0:sensor{c.bit}":
                store.ingest(observation(c, "ZERO", c.experiment_id))
        before = store.posterior()[0]
        audit = next(c for c in sc.candidates if c.experiment_id == "g0:audit")
        store.ingest(observation(audit, "ZERO", "audit"))
        after = store.posterior()[0]
        for bit in range(3):
            self.assertGreater(sum(p for h, p in enumerate(after) if not (h >> bit) & 1),
                               sum(p for h, p in enumerate(before) if not (h >> bit) & 1))

    def test_25_impossible_observation_is_not_silently_normalized(self):
        c = probe()
        only_zero = tuple(1.0 if h == 0 else 0.0 for h in range(16))
        with self.assertRaisesRegex(ValueError, "MODEL_CLASS_INADEQUATE"):
            conditioned(only_zero, c, "ONE")

    def test_26_paired_bootstrap_constant_effect(self):
        self.assertEqual(bootstrap([3.0] * 10, 100, 63059), [3.0, 3.0])

    def test_27_stale_or_manipulated_lock_is_rejected(self):
        m = load_manifest()
        metrics = {p: {"mean_loss": i} for i, p in enumerate(m["comparator_candidates"])}
        lock = {"source_sha256": "code", "manifest_sha256": digest(m),
                "development_seeds": m["development_seeds"], "development_metrics": metrics,
                "selected_policy": "hold"}
        self.assertEqual(validate_lock(lock, m, "code"), "hold")
        with self.assertRaisesRegex(ValueError, "STALE"):
            validate_lock(lock, m, "different-code")
        with self.assertRaises(ValueError):
            validate_lock(dict(lock, selected_policy="importance"), m, "code")

    def test_28_invalid_numeric_configuration_rejected(self):
        with self.assertRaises(ValueError):
            replace(probe(), accuracy=float("nan"))
        with self.assertRaises(ValueError):
            replace(probe(), null_probabilities=(0.8, 0.8, 0.0))
        with self.assertRaises(ValueError):
            Scenario(((0.0,) * 16,), (), ())


if __name__ == "__main__":
    unittest.main()
