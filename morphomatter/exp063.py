"""Experiment 063 pilot: finite diagnostic models, not a physical material model.

The selector receives Scenario and verified posteriors, never World.hidden.
All policies share the same evidence verifier and terminal decision rule.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
import math
from pathlib import Path
import random
from typing import Any

NUMERIC = ("ZERO", "ONE")
NULLS = ("INCONCLUSIVE", "FAILED", "EXECUTION_UNKNOWN")
OUTCOMES = NUMERIC + NULLS
POLICIES = ("hold", "random", "cheapest", "information_gain", "importance", "decision_value")


def digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def stream(seed: int, domain: str) -> random.Random:
    return random.Random(int(digest([seed, domain]), 16))


def load_manifest() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "experiments" / "exp063_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest["version"] != "063-pilot-v1":
        raise ValueError("Unsupported protocol version")
    return manifest


@dataclass(frozen=True)
class Task:
    task_id: str
    group: int
    bits: tuple[int, ...]
    operator: str
    weight: int

    def __post_init__(self) -> None:
        if not self.task_id or self.operator not in ("all", "any"):
            raise ValueError("Invalid task identity/operator")
        if not self.bits or any(type(b) is not int or b not in range(3) for b in self.bits):
            raise ValueError("Task bits must be in 0..2")
        if type(self.weight) is not int or self.weight <= 0:
            raise ValueError("Positive integer task weight required")

    def truth(self, hypothesis: int) -> bool:
        values = [bool((hypothesis >> b) & 1) for b in self.bits]
        return all(values) if self.operator == "all" else any(values)


@dataclass(frozen=True)
class Candidate:
    experiment_id: str
    group: int
    kind: str
    bit: int
    source_id: str
    scope: str
    cost: int
    accuracy: float
    null_probabilities: tuple[float, float, float] = (0.03, 0.03, 0.02)

    def __post_init__(self) -> None:
        if type(self.cost) is not int or self.cost <= 0:
            raise ValueError("Cost must be a positive integer; no epsilon/free dispatch")
        if self.kind not in ("sensor", "replication", "audit", "null"):
            raise ValueError("Unknown measurement kind")
        if not all((self.experiment_id, self.source_id, self.scope)) or self.bit not in range(3):
            raise ValueError("Invalid measurement identity or bit")
        if not math.isfinite(self.accuracy) or not 0 <= self.accuracy <= 1:
            raise ValueError("Invalid measurement accuracy")
        if (len(self.null_probabilities) != 3 or
                any(not math.isfinite(p) or p < 0 for p in self.null_probabilities) or
                sum(self.null_probabilities) >= 1):
            raise ValueError("Invalid failure distribution")

    def likelihood(self, hypothesis: int, outcome: str) -> float:
        if outcome in NULLS:
            return self.null_probabilities[NULLS.index(outcome)]
        if outcome not in NUMERIC:
            raise ValueError("Unknown observation outcome")
        success = 1 - sum(self.null_probabilities)
        if self.kind == "null":
            return success * 0.5
        fault = (hypothesis >> 3) & 1
        expected = fault if self.kind == "audit" else ((hypothesis >> self.bit) & 1)
        if self.kind == "sensor":
            expected ^= fault
        return success * (self.accuracy if NUMERIC[expected] == outcome else 1 - self.accuracy)


@dataclass(frozen=True)
class Observation:
    record_id: str
    experiment_id: str
    source_id: str
    scope: str
    outcome: str


@dataclass(frozen=True)
class Scenario:
    priors: tuple[tuple[float, ...], ...]
    tasks: tuple[Task, ...]
    candidates: tuple[Candidate, ...]
    initial: tuple[Observation, ...] = ()
    wrong_loss: float = 10.0
    hold_loss: float = 1.0

    def __post_init__(self) -> None:
        if not self.priors or any(len(p) != 16 or any(not math.isfinite(v) or v < 0 for v in p)
                                  or not math.isclose(sum(p), 1.0) for p in self.priors):
            raise ValueError("Each group needs a normalized 16-hypothesis prior")
        if any(not math.isfinite(v) or v <= 0 for v in (self.wrong_loss, self.hold_loss)):
            raise ValueError("Invalid decision loss")
        for items, key in ((self.tasks, "task_id"), (self.candidates, "experiment_id")):
            ids = [getattr(item, key) for item in items]
            if len(set(ids)) != len(ids):
                raise ValueError("Duplicate IDs would inflate evidence or task value")
            if any(type(item.group) is not int or item.group not in range(len(self.priors)) for item in items):
                raise ValueError("Unknown group")
        aliases: dict[str, tuple[Any, ...]] = {}
        for c in self.candidates:
            signature = (c.group, c.kind, c.bit, c.scope, c.accuracy, c.null_probabilities)
            if c.source_id in aliases and aliases[c.source_id] != signature:
                raise ValueError("One source cannot have incompatible measurement contracts")
            aliases[c.source_id] = signature


class EvidenceStore:
    """Fail-closed source binding, deduplication, quarantine, and revalidation."""
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self.candidates = {c.experiment_id: c for c in scenario.candidates}
        self.valid: dict[str, Observation] = {}
        self.attempted: set[str] = set()
        self.blocked: set[str] = set()
        self.events: list[dict[str, Any]] = []
        for observation in scenario.initial:
            self.ingest(observation)

    def ingest(self, observation: Observation) -> str:
        c = self.candidates.get(observation.experiment_id)
        if c is None or observation.source_id != c.source_id:
            status = "SOURCE_BINDING_MISMATCH"
        elif observation.scope != c.scope:
            status = "SCOPE_MISMATCH"
        elif observation.outcome not in OUTCOMES:
            status = "INVALID_OUTCOME"
        else:
            self.attempted.add(c.source_id)
            if c.source_id in self.blocked:
                status = "SOURCE_QUARANTINED"
            elif observation.outcome not in NUMERIC:
                status = observation.outcome
            elif c.source_id in self.valid:
                if self.valid[c.source_id].outcome == observation.outcome:
                    status = "DUPLICATE_SOURCE"
                else:
                    self.valid.pop(c.source_id)
                    self.blocked.add(c.source_id)
                    status = "SOURCE_CONFLICT"
            else:
                self.valid[c.source_id] = observation
                status = "VALID"
        self.events.append({"observation": asdict(observation), "status": status})
        return status

    def invalidate(self, source_id: str) -> None:
        self.valid.pop(source_id, None)
        self.blocked.add(source_id)
        self.events.append({"source_id": source_id, "status": "STALE"})

    def posterior(self) -> tuple[tuple[float, ...], ...]:
        # Recompute from prior, so invalidation does not leave hidden stale mass.
        probabilities = [tuple(p) for p in self.scenario.priors]
        for source in sorted(self.valid):
            observation = self.valid[source]
            c = self.candidates[observation.experiment_id]
            probabilities[c.group] = conditioned(probabilities[c.group], c, observation.outcome)
        return tuple(probabilities)

    def sources_by_group(self) -> tuple[tuple[str, ...], ...]:
        return tuple(tuple(sorted(s for s, o in self.valid.items()
                                  if self.candidates[o.experiment_id].group == g))
                     for g in range(len(self.scenario.priors)))


def conditioned(prior: tuple[float, ...], candidate: Candidate, outcome: str) -> tuple[float, ...]:
    masses = tuple(p * candidate.likelihood(h, outcome) for h, p in enumerate(prior))
    total = sum(masses)
    if total <= 0 or not math.isfinite(total):
        raise ValueError("MODEL_CLASS_INADEQUATE: impossible observation")
    return tuple(m / total for m in masses)


def branches(prior: tuple[float, ...], candidate: Candidate) -> list[tuple[str, float, tuple[float, ...]]]:
    result = []
    for outcome in OUTCOMES:
        probability = sum(p * candidate.likelihood(h, outcome) for h, p in enumerate(prior))
        if probability > 0:
            result.append((outcome, probability, conditioned(prior, candidate, outcome)))
    return result


def decision(task: Task, posterior: tuple[float, ...], scenario: Scenario) -> tuple[str, float, float]:
    p = sum(m for h, m in enumerate(posterior) if task.truth(h))
    risks = {"HOLD": scenario.hold_loss, "TRUE": scenario.wrong_loss * (1 - p),
             "FALSE": scenario.wrong_loss * p}
    action = "HOLD"
    for candidate in ("TRUE", "FALSE"):
        if risks[candidate] < risks[action] - 1e-12:
            action = candidate
    return action, task.weight * risks[action], p


def group_risk(scenario: Scenario, group: int, posterior: tuple[float, ...]) -> float:
    return sum(decision(t, posterior, scenario)[1] for t in scenario.tasks if t.group == group)


def entropy(p: tuple[float, ...]) -> float:
    return -sum(v * math.log2(v) for v in p if v > 0)


def candidate_score(scenario: Scenario, posteriors: tuple[tuple[float, ...], ...],
                    candidate: Candidate, policy: str) -> float:
    prior = posteriors[candidate.group]
    if policy == "importance":
        return sum(t.weight for t in scenario.tasks if t.group == candidate.group
                   and decision(t, prior, scenario)[0] == "HOLD") / candidate.cost
    outcomes = branches(prior, candidate)
    if policy == "information_gain":
        gain = entropy(prior) - sum(p * entropy(after) for _, p, after in outcomes)
    elif policy == "decision_value":
        gain = group_risk(scenario, candidate.group, prior) - sum(
            p * group_risk(scenario, candidate.group, after) for _, p, after in outcomes)
    else:
        raise ValueError("Scoring policy not supported")
    return max(0.0, gain) / candidate.cost


def select(scenario: Scenario, posteriors: tuple[tuple[float, ...], ...],
           attempted: set[str], remaining: int, policy: str,
           rng: random.Random) -> tuple[Candidate | None, dict[str, float], str]:
    if policy not in POLICIES:
        raise ValueError("Unknown policy")
    if policy == "hold":
        return None, {}, "ALL_HOLD"
    # Aliases are one candidate information source, including before acquisition.
    unique: dict[str, Candidate] = {}
    for c in sorted(scenario.candidates, key=lambda c: (c.cost, c.experiment_id)):
        if c.source_id not in attempted and c.cost <= remaining:
            unique.setdefault(c.source_id, c)
    feasible = sorted(unique.values(), key=lambda c: c.experiment_id)
    if not feasible:
        return None, {}, "NO_FEASIBLE_CANDIDATE"
    if policy == "random":
        return rng.choice(feasible), {}, "RANDOM_FEASIBLE"
    if policy == "cheapest":
        return min(feasible, key=lambda c: (c.cost, c.experiment_id)), {}, "CHEAPEST_FEASIBLE"
    scores = {c.experiment_id: candidate_score(scenario, posteriors, c, policy) for c in feasible}
    best = min(feasible, key=lambda c: (-scores[c.experiment_id], c.experiment_id))
    if scores[best.experiment_id] <= 1e-12:
        return None, scores, "NO_POSITIVE_EXPECTED_VALUE_UNDER_CURRENT_MODEL"
    return best, scores, policy.upper()


@dataclass(frozen=True)
class World:
    """Evaluator-only latent truth and stationary, source-keyed outcome tape."""
    scenario: Scenario
    hidden: tuple[int, ...]
    seed: int

    def observe(self, candidate: Candidate) -> Observation:
        rng = stream(self.seed, "measurement:" + candidate.source_id)
        draw = rng.random()
        cumulative = 0.0
        outcome = OUTCOMES[-1]
        for label in OUTCOMES:
            cumulative += candidate.likelihood(self.hidden[candidate.group], label)
            if draw < cumulative:
                outcome = label
                break
        return Observation("receipt:" + candidate.source_id, candidate.experiment_id,
                           candidate.source_id, candidate.scope, outcome)


def make_world(seed: int, manifest: dict[str, Any] | None = None) -> World:
    m = manifest or load_manifest()
    rng = stream(seed, "world")
    groups = m["groups"]
    if m["claims_per_group"] != 3 or m["hypotheses_per_group"] != 16:
        raise ValueError("Only the frozen three-claim/fault-bit fixture is implemented")
    q = m["fault_prior"]
    prior = tuple((q if (h >> 3) & 1 else 1 - q) / 8 for h in range(16))
    hidden = tuple(rng.randrange(8) | (int(rng.random() < q) << 3) for _ in range(groups))
    tasks: list[Task] = []
    candidates: list[Candidate] = []
    failures = tuple(m["outcome_failure_probabilities"][o] for o in NULLS)
    for g in range(groups):
        scope = f"synthetic-group-{g}:scope-v1"
        pattern = [((0,), "all"), ((1,), "all"), ((2,), "all"),
                   ((0, 1), "all"), ((1, 2), "any"), ((0, 2), "all")]
        for i, (bits, op) in enumerate(pattern):
            tasks.append(Task(f"g{g}:t{i}", g, bits, op, rng.choice(m["task_weights"])))
        for bit in range(3):
            candidates.append(Candidate(f"g{g}:sensor{bit}", g, "sensor", bit,
                                        f"g{g}:sensor-source{bit}", scope, 1,
                                        m["sensor_accuracy"], failures))
            candidates.append(Candidate(f"g{g}:replicate{bit}", g, "replication", bit,
                                        f"g{g}:independent-source{bit}", scope, rng.choice((2, 4)),
                                        m["replication_accuracy"], failures))
        candidates.append(Candidate(f"g{g}:audit", g, "audit", 0, f"g{g}:calibration-source",
                                    scope, 2, m["audit_accuracy"], failures))
        candidates.append(Candidate(f"g{g}:alias0", g, "sensor", 0, f"g{g}:sensor-source0",
                                    scope, 1, m["sensor_accuracy"], failures))
        candidates.append(Candidate(f"g{g}:null", g, "null", 0, f"g{g}:uninformative-source",
                                    scope, 1, 0.5, failures))
    scenario = Scenario(tuple(prior for _ in range(groups)), tuple(tasks), tuple(candidates),
                        wrong_loss=m["wrong_loss"], hold_loss=m["hold_loss"])
    world = World(scenario, hidden, seed)
    initial = []
    for g in range(groups):
        if rng.random() < m["initial_sensor_probability_per_group"]:
            for c in candidates:
                if c.group == g and c.experiment_id == f"g{g}:sensor{c.bit}":
                    observation = world.observe(c)
                    initial.append(observation)
                    for k in range(m["initial_duplicate_reports_per_sensor"]):
                        initial.append(replace(observation, record_id=observation.record_id + f":copy{k}"))
    return replace(world, scenario=replace(scenario, initial=tuple(initial)))


class BudgetLedger:
    def __init__(self, budget: int) -> None:
        if type(budget) is not int or budget < 0:
            raise ValueError("Nonnegative integer budget required")
        self.initial = budget
        self.remaining = budget
        self.dispatched_sources: set[str] = set()
        self.events: list[dict[str, Any]] = []

    def append(self, payload: dict[str, Any]) -> None:
        previous = self.events[-1]["hash"] if self.events else "GENESIS"
        self.events.append({"previous": previous, "payload": payload,
                            "hash": digest([previous, payload])})

    def reserve(self, candidate: Candidate, prediction: dict[str, Any]) -> None:
        if candidate.source_id in self.dispatched_sources:
            raise ValueError("Duplicate source dispatch")
        if candidate.cost > self.remaining:
            raise ValueError("Insufficient budget")
        before = self.remaining
        self.remaining -= candidate.cost
        self.dispatched_sources.add(candidate.source_id)
        self.append({"event": "SELECTION", "experiment_id": candidate.experiment_id,
                     "source_id": candidate.source_id, "budget_before": before,
                     "reserved_cost": candidate.cost, "budget_after": self.remaining,
                     "prediction_before_execution": prediction})


def check_chain(events: list[dict[str, Any]]) -> bool:
    previous = "GENESIS"
    for event in events:
        if event["previous"] != previous or event["hash"] != digest([previous, event["payload"]]):
            return False
        previous = event["hash"]
    return True


def invalid_source_uses(decisions: list[dict[str, Any]], store: EvidenceStore) -> int:
    return sum(1 for d in decisions if d["action"] != "HOLD"
               and any(s not in store.valid or s in store.blocked for s in d["evidence_sources"]))


def run_policy(world: World, policy: str, budget: int = 12, maximum_steps: int = 12) -> dict[str, Any]:
    if policy not in POLICIES or type(maximum_steps) is not int or maximum_steps < 0:
        raise ValueError("Invalid policy/step limit")
    scenario = world.scenario
    store = EvidenceStore(scenario)
    ledger = BudgetLedger(budget)
    rng = stream(world.seed, "policy:" + policy)
    reason = "STEP_LIMIT"
    for step in range(maximum_steps):
        post = store.posterior()
        candidate, scores, reason = select(scenario, post, store.attempted | ledger.dispatched_sources,
                                           ledger.remaining, policy, rng)
        if candidate is None:
            break
        predicted = {o: p for o, p, _ in branches(post[candidate.group], candidate)}
        ledger.reserve(candidate, {"step": step, "reason": reason, "scores": scores,
                                   "outcome_probabilities": predicted,
                                   "posterior_hash": digest(post),
                                   "candidate_set_hash": digest([asdict(c) for c in scenario.candidates]),
                                   "valid_sources": sorted(store.valid)})
        observation = world.observe(candidate)  # Only evaluator boundary accesses truth.
        status = store.ingest(observation)
        ledger.append({"event": "RECEIPT", "observation": asdict(observation),
                       "verification_status": status, "actual_cost": candidate.cost})
        if ledger.remaining == 0:
            reason = "BUDGET_LIMIT"
            break
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
    return {"world_id": world.seed, "policy": policy, "loss": loss, "correct": correct,
            "wrong": wrong, "hold": holds, "spent": budget - ledger.remaining,
            "steps": len(ledger.dispatched_sources), "stop_reason": reason,
            "known_invalid_leakage": invalid_source_uses(decisions, store),
            "budget_violation": int(ledger.remaining < 0 or len(ledger.dispatched_sources) > maximum_steps),
            "decisions": decisions, "verification_events": store.events,
            "ledger": ledger.events, "ledger_chain_valid": check_chain(ledger.events)}
