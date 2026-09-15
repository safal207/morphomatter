# Experiment 060 — Causal State Fingerprint / Replication Passport

## Goal

Define a compact, inspectable **replication passport** that certifies whether two runs begin from causally equivalent states before the same protocol is applied.

The central problem is that matching visible inputs is not enough:

\[
U^{(a)}_{0:T}=U^{(b)}_{0:T}
\not\Rightarrow
Outcome_a=Outcome_b
\]

if hidden state, history, interface, defects, gradients, or preconditioning differ.

Experiment 060 therefore asks:

> Can MorphoMatter construct a minimal causal fingerprint of the starting state that predicts whether a protocol can be meaningfully replicated?

---

## Core object: Replication Passport

For run \(r\), define:

\[
Passport_r = \{F_r, B_r, H_r, E_r, P_r\}
\]

where:

- \(F_r\) — causal state fingerprint;
- \(B_r\) — validity bounds / action envelope;
- \(H_r\) — compressed causal history;
- \(E_r\) — evidence references supporting the fingerprint;
- \(P_r\) — protocol metadata and required preconditions.

The passport must be inspectable and replayable. It is not a confidence label alone.

---

## Candidate fingerprint channels

The fingerprint should include only variables that materially affect transition behavior, for example:

### Material state
- order parameter;
- defect density;
- local connectivity;
- particle-property distribution;
- mobility / trapped fraction.

### Environment
- temperature-like coordinate;
- pressure-like coordinate;
- ionic-strength / screening surrogate;
- external field amplitudes;
- spatial gradients.

### Interface
- contact-angle-like affinity;
- effective roughness;
- boundary geometry;
- source/sink topology.

### History
- previous phase;
- dwell time;
- ramp rate;
- recent damage / recovery cycle;
- prior intervention sequence.

### Dynamic state
- frontier velocity;
- nucleation activity;
- causal-field summary;
- attractor-basin membership;
- predictive latent state \(Z_t\).

---

## Causal equivalence

Two runs are considered causally equivalent only relative to a protocol and target observable.

Define:

\[
Eq(a,b\mid U,Y)=1
\]

if, under protocol \(U\), the relevant future distribution of outcome \(Y\) is sufficiently close:

\[
D\big(P(Y\mid F_a,U), P(Y\mid F_b,U)\big) \le \epsilon
\]

The important consequence is:

> There is no universal state fingerprint independent of the question being asked.

A variable irrelevant for one transition may be decisive for another.

---

## Minimal sufficient fingerprint

The experiment should search for the smallest fingerprint \(F^*\) that preserves predictive equivalence:

\[
F^* = \arg\min_F Complexity(F)
\]

subject to:

\[
P(Y\mid U,F) \approx P(Y\mid U,H_{full})
\]

This connects directly to Experiment 059 history compression.

The goal is not maximal logging. The goal is **minimal causally sufficient logging**.

---

## Experimental design

### Phase A — Reference run

Create a successful reference trajectory with full-state logging:

```text
full initial state
→ preconditioning
→ protocol
→ transition
→ outcome
```

Freeze the full evidence package.

### Phase B — Matched visible protocol, perturbed hidden state

Generate replicas where the visible control sequence is identical but exactly one hidden dimension changes:

- previous phase;
- dwell time;
- defect distribution;
- interface state;
- gradient field;
- preconditioning order;
- damage history.

Measure when protocol equivalence breaks.

### Phase C — Fingerprint discovery

Learn or derive candidate fingerprints from the full history.

Compare:

1. visible-protocol-only fingerprint;
2. static macrostate fingerprint;
3. full-state fingerprint;
4. compressed causal fingerprint;
5. random matched-size fingerprint.

### Phase D — Cross-run replication test

For unseen runs, predict before execution:

- `EQUIVALENT`;
- `NOT_EQUIVALENT`;
- `INSUFFICIENT_EVIDENCE`.

Then execute the protocol and compare the prediction with the observed transition outcome.

---

## Replication Passport schema

Suggested machine-readable structure:

```yaml
passport_version: 0.1
protocol_id: protocol-A
fingerprint:
  state_features: ...
  history_features: ...
  interface_features: ...
  dynamic_features: ...
validity_bounds:
  environment: ...
  action_envelope: ...
evidence:
  source_runs: ...
  proof_dependencies: ...
  freshness: ...
equivalence_claim:
  target_observable: ...
  tolerance: ...
  confidence: ...
status: EQUIVALENT | NOT_EQUIVALENT | INSUFFICIENT_EVIDENCE | STALE
```

---

## Proof-carrying replication

A replication claim should carry its own support:

```text
"same protocol"
    ↓
state passport
    ↓
causal-equivalence test
    ↓
expected outcome distribution
    ↓
run
    ↓
observed evidence
```

This upgrades replication from:

> “We followed the same recipe.”

to:

> “We verified that the causally relevant initial state and history were equivalent within declared bounds.”

---

## Staleness and invalidation

A passport is valid only while its supporting evidence and causal assumptions remain valid.

If a supporting proof becomes stale or falsified:

\[
Invalidate(Proof_i)
\Rightarrow
Reevaluate(Passport_j)
\]

for every passport depending on that proof.

A stale passport must not silently remain `EQUIVALENT`.

Possible statuses:

- `VALID`;
- `STALE`;
- `FALSIFIED`;
- `PARTIALLY_SUPPORTED`;
- `INSUFFICIENT_EVIDENCE`.

---

## Metrics

### Replication-equivalence accuracy
How often the passport correctly predicts whether matched protocols will produce equivalent outcomes.

### False-equivalence rate
Critical metric:

\[
FER = P(\hat Eq=1 \mid Eq=0)
\]

This should be very low.

### Fingerprint compression ratio

\[
CR = \frac{Size(full\ history)}{Size(fingerprint)}
\]

subject to preserved predictive performance.

### Transfer accuracy
Can a fingerprint discovered in one environment remain useful in nearby environments?

### Calibration
Does stated equivalence confidence match empirical replication success?

### Repair cost
When a passport becomes stale, how much new evidence is required to restore it?

### Invalid-trust leakage
Target:

```text
invalid_trust_leakage = 0
```

---

## Negative controls

1. **Protocol-only passport** — omit history and hidden state.
2. **Random fingerprint** — same dimensionality, random features.
3. **Shuffled history** — preserve marginal values but destroy temporal order.
4. **Omit one known causal precondition** — verify that equivalence confidence drops.
5. **Regime shift after passport creation** — verify stale detection.
6. **Matched macrostate, different latent basin** — test whether static observables are insufficient.
7. **Unknown confounder** — require `INSUFFICIENT_EVIDENCE` rather than forced equivalence.

---

## Strong success criterion

Experiment 060 succeeds only if the causal fingerprint:

- predicts replication success better than visible-protocol matching;
- remains compact relative to full history;
- identifies at least some non-equivalent states that look macroscopically similar;
- degrades or abstains under hidden confounding or regime shift;
- supports independent replay from its evidence references.

A useful verdict could be:

```text
CAUSAL_FINGERPRINT_PREDICTS_PROTOCOL_EQUIVALENCE
```

A valid negative outcome could be:

```text
NO_COMPACT_CAUSAL_FINGERPRINT_FOUND
```

or:

```text
STATIC_STATE_INSUFFICIENT_HISTORY_REQUIRED
```

---

## Relation to previous experiments

Experiment 059 established that identical visible protocols can diverge because of hidden preconditions.

Experiment 060 turns that insight into an operational artifact:

```text
hidden preconditions
→ causal fingerprint
→ replication passport
→ protocol-equivalence claim
→ evidence-backed replication
```

It also connects to:

- Exp019 — memory and hysteresis;
- Exp023 — causal fractal memory;
- Exp028 / 051 — world models and predictive state;
- Exp055 — proof-carrying control;
- Exp056 — proof chains;
- Exp057 — proof repair;
- Exp058 — proof portfolio optimization;
- Exp059 — hidden preconditions and protocol equivalence.

---

## Scientific boundary

This experiment is currently a synthetic/software research plan.

A successful simulation result would not by itself prove that a real material has the same sufficient fingerprint. Physical use requires independently measured state variables, calibrated sensors, explicit uncertainty, preregistered tolerances, and external replication.

---

## Core principle

> Replication is not repetition of commands. Replication is restoration of the causally relevant state.

And in the language of MorphoMatter:

> Every external proof that establishes state equivalence reduces the cost of trusting the next transition claim.
