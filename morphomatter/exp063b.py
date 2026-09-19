"""063B: bounded nonadaptive pair lookahead with receding-horizon execution.

The archived 063 module is unchanged. All comparisons use this same guarded
runner. Pair search is exact for its two-experiment scoring rule, not a globally
optimal policy or full outcome-adaptive Bellman planner.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from itertools import combinations
import math
import random
from typing import Any

from morphomatter.exp063 import (
    BudgetLedger, Candidate, EvidenceStore, Observation, POLICIES as BASE_POLICIES,
    Scenario, World, branches, check_chain, decision, digest, invalid_source_uses,
    make_world, select, stream,
)

POLICIES = BASE_POLICIES + ("pair_value",)
EPS = 1e-12


def validate_scenario(scenario: Scenario) -> None:
    for c in scenario.candidates:
        if type(c.bit) is not int or c.bit not in range(3):
            raise ValueError("Candidate bit must be an integer in 0..2, not bool/float")


def scope_world(world: World) -> World:
    """Bind evidence to one world without changing the source-keyed outcome tape.

This namespace is identity checking, not a signature or a security sandbox.
The evaluator still owns the seed and truth; the selector sees an opaque scope.
"""
    suffix = "|world:" + digest(["063b-scope", world.seed])
    original = {c.experiment_id: c for c in world.scenario.candidates}
    candidates = tuple(replace(c, scope=c.scope + suffix) for c in world.scenario.candidates)
    initial = tuple(replace(o, scope=o.scope + suffix)
                    if o.experiment_id in original and o.scope == original[o.experiment_id].scope else o
                    for o in world.scenario.initial)
    return replace(world, scenario=replace(world.scenario, candidates=candidates, initial=initial))


def make_scoped_world(seed: int) -> World:
    return scope_world(make_world(seed))


def unavailable(store: EvidenceStore, ledger: BudgetLedger) -> set[str]:
    # A revoked source can be blocked before its first observation.
    return store.attempted | store.blocked | ledger.dispatched_sources


def accept_receipt(store: EvidenceStore, selected: Candidate, receipt: Observation) -> str:
    expected = (selected.experiment_id, selected.source_id, selected.scope)
    actual = (receipt.experiment_id, receipt.source_id, receipt.scope)
    if expected != actual:
        status = "RECEIPT_DISPATCH_MISMATCH"
        store.events.append({"observation": asdict(receipt), "status": status,
                             "expected_experiment_id": selected.experiment_id,
                             "expected_source_id": selected.source_id,
                             "expected_scope": selected.scope})
        return status
    return store.ingest(receipt)


def feasible_candidates(scenario: Scenario, excluded: set[str], budget: int) -> tuple[Candidate, ...]:
    unique: dict[str, Candidate] = {}
    for c in sorted(scenario.candidates, key=lambda c: (c.cost, c.experiment_id)):
        if c.source_id not in excluded and c.cost <= budget:
            unique.setdefault(c.source_id, c)
    return tuple(sorted(unique.values(), key=lambda c: c.experiment_id))


class PairScorer:
    """Risk from unnormalized hypothesis masses; nulls merge only for scoring.

Summing posterior risk times outcome probability equals risk on unnormalized
masses, avoiding repeated divisions. Independent-group pair gains add. Same-group
likelihoods are multiplied conditional on the declared shared-fault hypothesis.
"""
    def __init__(self, scenario: Scenario) -> None:
        validate_scenario(scenario)
        self.scenario = scenario
        self.tasks = {
            g: tuple((t.weight, tuple(h for h in range(16) if t.truth(h)))
                     for t in scenario.tasks if t.group == g)
            for g in range(len(scenario.priors))
        }
        self.likelihoods = {
            c.experiment_id: (
                tuple(c.likelihood(h, "ZERO") for h in range(16)),
                tuple(c.likelihood(h, "ONE") for h in range(16)),
                tuple(sum(c.null_probabilities) for _ in range(16)),
            ) for c in scenario.candidates
        }
        self.cache: dict[tuple[Any, ...], float] = {}
        self.exact_evaluations = 0

    def mass_risk(self, group: int, masses: tuple[float, ...]) -> float:
        total = math.fsum(masses)
        if total <= 0:
            return 0.0
        hold = self.scenario.hold_loss * total
        wrong = self.scenario.wrong_loss
        result = 0.0
        for weight, truth_indices in self.tasks[group]:
            positive = math.fsum(masses[h] for h in truth_indices)
            negative = max(0.0, total - positive)
            result += weight * min(hold, wrong * positive, wrong * negative)
        return result

    def expected_risk(self, prior: tuple[float, ...], a: Candidate,
                      b: Candidate | None = None) -> float:
        if b is not None and (a.source_id == b.source_id or a.group != b.group):
            raise ValueError("Joint mass calculation needs distinct sources in one group")
        key = (a.experiment_id, b.experiment_id if b else None, prior)
        if key in self.cache:
            return self.cache[key]
        expected = 0.0
        la = self.likelihoods[a.experiment_id]
        lb = self.likelihoods[b.experiment_id] if b else ((1.0,) * 16,)
        for first in la:
            for second in lb:
                masses = tuple(p * l1 * l2 for p, l1, l2 in zip(prior, first, second))
                expected += self.mass_risk(a.group, masses)
        self.cache[key] = expected
        self.exact_evaluations += 1
        return expected

    def score_plans(self, posteriors: tuple[tuple[float, ...], ...],
                    feasible: tuple[Candidate, ...], budget: int,
                    steps_left: int) -> list[dict[str, Any]]:
        if steps_left <= 0:
            return []
        risks = {g: self.mass_risk(g, p) for g, p in enumerate(posteriors)}
        gains = {}
        plans = []
        for c in feasible:
            gains[c.experiment_id] = max(0.0, risks[c.group] - self.expected_risk(posteriors[c.group], c))
            gain = gains[c.experiment_id]
            plans.append({"plan": [c.experiment_id], "gain": gain,
                          "planned_cost": c.cost, "score": gain / c.cost})
        if steps_left >= 2:
            for a, b in combinations(feasible, 2):
                cost = a.cost + b.cost
                if cost > budget:
                    continue
                if a.group == b.group:
                    gain = max(0.0, risks[a.group] - self.expected_risk(posteriors[a.group], a, b))
                else:
                    gain = gains[a.experiment_id] + gains[b.experiment_id]
                plans.append({"plan": [a.experiment_id, b.experiment_id], "gain": gain,
                              "planned_cost": cost, "score": gain / cost})
        return plans

    def choose(self, posteriors: tuple[tuple[float, ...], ...], excluded: set[str],
               budget: int, steps_left: int) -> tuple[Candidate | None, list[dict[str, Any]], str]:
        feasible = feasible_candidates(self.scenario, excluded, budget)
        plans = self.score_plans(posteriors, feasible, budget, steps_left)
        if not plans:
            return None, [], "NO_FEASIBLE_CANDIDATE"
        # Exact numerical score first; deterministic tuple order for exact ties.
        plans.sort(key=lambda p: (-p["score"], tuple(p["plan"])))
        if plans[0]["score"] <= EPS:
            return None, plans, "NO_POSITIVE_EXPECTED_VALUE_UNDER_CURRENT_MODEL"
        first = plans[0]["plan"][0]
        return next(c for c in feasible if c.experiment_id == first), plans, "PAIR_LOOKAHEAD_REPLAN"


def run_guarded(world: World, policy: str, budget: int = 12,
                maximum_steps: int = 12) -> dict[str, Any]:
    if policy not in POLICIES or type(maximum_steps) is not int or maximum_steps < 0:
        raise ValueError("Invalid policy/step limit")
    scenario = world.scenario
    validate_scenario(scenario)
    store = EvidenceStore(scenario)
    ledger = BudgetLedger(budget)
    rng = stream(world.seed, "policy:" + policy)
    scorer = PairScorer(scenario) if policy == "pair_value" else None
    reason = "STEP_LIMIT"
    rejections = 0
    pair_selections = 0
    for step in range(maximum_steps):
        post = store.posterior()
        excluded = unavailable(store, ledger)
        if scorer:
            candidate, plans, reason = scorer.choose(post, excluded, ledger.remaining, maximum_steps - step)
            scores = {}
        else:
            candidate, scores, reason = select(scenario, post, excluded, ledger.remaining, policy, rng)
            plans = []
        if candidate is None:
            break
        predicted = {o: p for o, p, _ in branches(post[candidate.group], candidate)}
        chosen_plan = plans[0] if plans else {"plan": [candidate.experiment_id], "planned_cost": candidate.cost}
        pair_selections += int(len(chosen_plan["plan"]) == 2)
        ledger.reserve(candidate, {
            "step": step, "reason": reason, "scores": scores,
            "selected_plan": chosen_plan, "plan_scores": plans,
            "outcome_probabilities": predicted, "posterior_hash": digest(post),
            "candidate_set_hash": digest([asdict(c) for c in scenario.candidates]),
            "excluded_sources": sorted(excluded), "valid_sources": sorted(store.valid),
        })
        receipt = world.observe(candidate)  # Evaluator boundary; no truth input to the selector.
        status = accept_receipt(store, candidate, receipt)
        rejections += int(status == "RECEIPT_DISPATCH_MISMATCH")
        ledger.append({"event": "RECEIPT", "observation": asdict(receipt),
                       "verification_status": status, "actual_cost": candidate.cost})
        if ledger.remaining == 0:
            reason = "BUDGET_LIMIT"
            break
    else:
        reason = "STEP_LIMIT"
    post = store.posterior()
    sources = store.sources_by_group()
    decisions = []
    loss = 0.0
    wrong = correct = holds = 0
    for task in scenario.tasks:
        action, risk, p = decision(task, post[task.group], scenario)
        if policy == "hold":
            action, risk = "HOLD", task.weight * scenario.hold_loss
        if action == "HOLD":
            holds += 1
            loss += task.weight * scenario.hold_loss
        elif (action == "TRUE") == task.truth(world.hidden[task.group]):
            correct += 1
        else:
            wrong += 1
            loss += task.weight * scenario.wrong_loss
        decisions.append({"task_id": task.task_id, "action": action, "probability_true": p,
                          "estimated_loss": risk, "evidence_sources": list(sources[task.group])})
    return {
        "world_id": world.seed, "policy": policy, "loss": loss, "correct": correct,
        "wrong": wrong, "hold": holds, "spent": budget - ledger.remaining,
        "steps": len(ledger.dispatched_sources), "stop_reason": reason,
        "known_invalid_leakage": invalid_source_uses(decisions, store),
        "receipt_rejections": rejections, "pair_selections": pair_selections,
        "exact_risk_evaluations": scorer.exact_evaluations if scorer else None,
        "budget_violation": int(ledger.remaining < 0 or len(ledger.dispatched_sources) > maximum_steps),
        "decisions": decisions, "verification_events": store.events,
        "ledger": ledger.events, "ledger_chain_valid": check_chain(ledger.events),
    }
