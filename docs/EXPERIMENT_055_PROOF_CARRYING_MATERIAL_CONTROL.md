# Experiment 055 — Proof-Carrying Material Control

## Goal

Turn material control from opaque action selection into an evidence-carrying process in which every intervention is accompanied by a machine-checkable claim about why the action is justified, what it is expected to do, what would falsify that expectation, and what evidence was actually observed afterward.

The central principle is:

> Every external proof reduces the trust cost of the next step.

This experiment therefore asks whether control can become progressively more trustworthy as the controller accumulates verified evidence rather than merely accumulating model confidence.

## Core idea

Instead of issuing only an action

\[
U_t
\]

the controller emits a proof packet

\[
P_t = (S_t, H_t, U_t, \hat Y_{t+1:t+h}, B_t, F_t, E_t)
\]

where:

- \(S_t\) — observed current state;
- \(H_t\) — causal hypothesis supporting the action;
- \(U_t\) — proposed intervention;
- \(\hat Y_{t+1:t+h}\) — predicted outcome over a bounded horizon;
- \(B_t\) — applicability bounds and assumptions;
- \(F_t\) — falsification condition;
- \(E_t\) — evidence references used to justify the action.

The action is authorized only if the proof packet passes validation.

## Architecture

```text
Observation
    ↓
Causal Model
    ↓
Candidate Intervention
    ↓
Proof Packet
    ↓
Proof Validator
    ↓
AUTHORIZED / REJECTED / NEEDS_DISCOVERY
    ↓
Execute Intervention
    ↓
Observed Outcome
    ↓
Evidence Ledger
    ↓
Model Update
```

## Proof packet

Each proposed control step must record at least:

```text
action_id
state_hash
model_version
causal_hypothesis
intervention
predicted_outcome
prediction_horizon
confidence_or_uncertainty
applicability_bounds
falsification_condition
expected_cost
expected_risk
evidence_refs
```

After execution, the packet is extended with:

```text
observed_outcome
prediction_error
falsified_or_supported
new_evidence_ref
next_action_authority
```

## Authorization rule

A candidate action is executable only if all required conditions hold:

\[
Authorize(U_t)=
ValidEvidence
\land InBounds
\land Reachable
\land RiskAcceptable
\land PredictionTestable
\]

Otherwise the controller must return one of:

```text
REJECTED_OUT_OF_BOUNDS
REJECTED_UNSUPPORTED_CAUSAL_CLAIM
REJECTED_UNTESTABLE_PREDICTION
TARGET_UNREACHABLE_WITHIN_ACTION_ENVELOPE
NEEDS_DISCOVERY_BEFORE_CONTROL
```

## Main hypothesis

A proof-carrying controller should reduce silent model drift and unsupported actions relative to a controller that acts only from policy score or model confidence.

The expected advantage is not necessarily lower immediate intervention cost. It is lower cumulative failure and trust cost across a sequence of decisions.

## Experimental conditions

Compare at least five controllers:

1. **Open-loop control** — fixed policy, no proof packet.
2. **Predictive control** — uses a world model but emits no explicit causal proof.
3. **Confidence-gated control** — executes only above a model confidence threshold.
4. **Proof-carrying control** — full proof packet and validation.
5. **Proof-carrying + discovery fallback** — rejects weak actions and actively requests a discriminating experiment when evidence is insufficient.

## Test scenarios

### A. Stable regime

The underlying transition law stays fixed.

Measure whether proof overhead harms or improves ordinary control performance.

### B. Hidden regime shift

After successful control, silently change one causal dependency.

Expected behavior:

```text
prediction mismatch
→ proof failure
→ action authority revoked
→ discovery request
→ model update
→ new proof packet
→ control resumes
```

### C. Confounded evidence

Provide observations compatible with two different causal explanations.

Correct behavior is not forced control, but:

```text
NEEDS_DISCOVERY_BEFORE_CONTROL
```

### D. Unreachable target

Set a target outside the bounded action envelope.

Correct behavior:

```text
TARGET_UNREACHABLE_WITHIN_ACTION_ENVELOPE
```

### E. False high confidence

Construct a model that is highly confident but causally wrong.

This separates confidence from proof quality.

### F. Evidence corruption / stale evidence

Invalidate or replace an evidence dependency and test whether downstream proof packets are also invalidated.

## Evidence dependency graph

Each proof packet should form a dependency graph:

```text
Evidence E1
    ↓
Hypothesis H1
    ↓
Prediction P1
    ↓
Intervention U1
    ↓
Observed Result R1
    ↓
Evidence E2
    ↓
Next Hypothesis H2
```

This gives the project a concrete implementation of the principle:

> each external proof reduces the trust cost of the next step.

But a failed proof must increase trust cost again rather than being silently ignored.

## Evidence ledger

Every intervention produces an immutable logical record:

```text
proof_id
parent_proof_ids
state_before
hypothesis
prediction
intervention
falsification_rule
state_after
result
verdict
```

Possible verdicts:

```text
SUPPORTED_WITHIN_BOUNDS
FALSIFIED
INCONCLUSIVE
OUT_OF_DISTRIBUTION
NON_IDENTIFIABLE
```

## Trust-cost metric

Define a synthetic trust cost for a sequence of actions:

\[
TC = \sum_t (
C_{verification,t}
+ C_{failure,t}
+ C_{recovery,t}
+ C_{unsupported,t}
)
\]

The main claim of this experiment should be evaluated on cumulative trust cost, not just target-reaching speed.

A proof-carrying method succeeds only if its extra verification cost is offset by lower unsupported-action, failure, or recovery cost in at least some preregistered regimes.

## Metrics

- target success rate;
- intervention cost;
- cumulative trust cost;
- unsupported action count;
- false authorization rate;
- proof rejection precision;
- detection delay after regime shift;
- recovery time after falsification;
- fraction of actions with replayable evidence;
- calibration between predicted and observed outcomes;
- evidence reuse rate across consecutive actions.

## Critical ablations

Remove one component at a time:

- no falsification condition;
- no applicability bounds;
- no evidence lineage;
- no causal hypothesis;
- no model-version binding;
- no stale-evidence invalidation;
- no discovery fallback;
- confidence only.

The goal is to identify which proof components actually reduce failure or trust cost.

## Required negative results

The experiment must explicitly permit the following outcomes:

```text
PROOF_OVERHEAD_EXCEEDS_BENEFIT
CONFIDENCE_GATE_MATCHES_PROOF_CONTROL
CAUSAL_PROOF_DOES_NOT_REDUCE_FAILURE
DISCOVERY_FALLBACK_TOO_EXPENSIVE
EVIDENCE_REUSE_PROVIDES_NO_ADVANTAGE
MODEL_CLASS_INADEQUATE
NON_IDENTIFIABLE_UNDER_CURRENT_INTERVENTIONS
```

These are valid scientific outcomes and must not be reframed as success.

## Success criterion

A bounded positive result requires all of the following:

1. proof-carrying control lowers preregistered cumulative trust cost or false-authorization rate in at least one difficult regime;
2. the gain survives at least one important ablation/control comparison;
3. every claimed improvement is replayable from the evidence ledger;
4. the controller correctly refuses at least some unsupported or unreachable actions;
5. no claim is made beyond the synthetic model used in the experiment.

## Interpretation boundary

A positive result would support only the claim that an explicit proof/evidence layer can improve reliability of synthetic material-control decisions under the tested model.

It would **not** prove:

- safe control of real materials;
- physical causal validity outside the simulator;
- autonomous scientific truth discovery;
- universal guarantees of correctness;
- that a model-generated explanation is itself a proof without external evidence.

Physical claims require independent measurement and replication.

## Relation to MorphoMatter

This experiment connects causal discovery, world-model prediction, control, and reproducible evidence:

```text
understand
   ↓
predict
   ↓
justify
   ↓
act
   ↓
measure
   ↓
falsify or support
   ↓
reuse verified evidence
```

It turns the MorphoMatter controller from a policy that says *what to do* into a system that must also answer:

> Why is this action justified now, what evidence supports it, and what observation would make us stop trusting it?

## Next experiment

### Experiment 056 — Proof-Chained Autonomous Material Science

Test whether a sequence of independently checkable proof packets can support a longer discovery trajectory in which every new hypothesis, experiment, and control step must inherit valid evidence from previous steps.

The core question becomes:

\[
Proof_1 \rightarrow Proof_2 \rightarrow ... \rightarrow Proof_n
\]

Can the system accumulate useful knowledge while preventing an early unsupported assumption from silently contaminating the rest of the chain?
