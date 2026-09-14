# Experiment 056 — Proof-Chained Autonomous Material Science

## Goal

Test whether a long scientific discovery/control trajectory can remain trustworthy when every conclusion depends on prior evidence, including cases where an early proof later fails.

The system must not merely accumulate successful-looking results. It must preserve explicit provenance and propagate invalidation through the dependency graph.

## Core principle

Each accepted result becomes evidence for later decisions:

\[
Proof_1 \rightarrow Proof_2 \rightarrow \cdots \rightarrow Proof_n
\]

But trust is conditional, not permanent. If an upstream proof is falsified, all downstream conclusions that depend on it must be downgraded until independently revalidated.

\[
Invalidate(Proof_i) \Rightarrow Recheck(Descendants(Proof_i))
\]

This operationalizes the MorphoMatter principle:

> Every external proof can reduce the cost of the next trust decision, but only while its provenance and validity remain intact.

## Proof dependency graph

Represent scientific claims and control decisions as a directed acyclic evidence graph:

\[
G_P=(V_P,E_P)
\]

Each proof node stores:

- hypothesis or claim;
- exact experiment/intervention;
- predicted result;
- observed result;
- model/version/seed/configuration;
- applicability bounds;
- falsification condition;
- evidence artifacts;
- upstream dependencies;
- confidence/status;
- timestamp or sequence index.

Recommended node states:

- `PROVISIONAL`
- `SUPPORTED`
- `FALSIFIED`
- `STALE`
- `DEPENDENCY_INVALIDATED`
- `REVALIDATED`
- `NON_IDENTIFIABLE`

## Closed-loop architecture

```text
Hypothesis
   ↓
Experiment design
   ↓
Prediction + falsification condition
   ↓
Execution
   ↓
External evidence / replay artifact
   ↓
Proof node
   ↓
Dependency graph update
   ↓
Scientific/control decision
   ↓
Next hypothesis
```

With failure propagation:

```text
upstream proof fails
        ↓
identify descendants
        ↓
mark dependent claims invalid/stale
        ↓
stop proof-dependent control
        ↓
select minimal revalidation experiments
        ↓
restore or revise chain
```

## Main research question

Can the system complete a multi-step scientific/control trajectory while preserving causal and evidential integrity better than a controller that only stores scalar confidence scores or successful outcomes?

## Experimental scenarios

### 1. Clean proof chain

Construct a sequence where all upstream assumptions remain valid.

Measure whether later experiments correctly reuse earlier evidence rather than repeating redundant validation.

Expected benefit:

\[
TrustCost_{n+1} < TrustCost_n
\]

when earlier proof remains valid and relevant.

### 2. Delayed upstream falsification

Allow the system to build several downstream conclusions from `Proof_1`, then introduce new evidence that falsifies `Proof_1`.

Required behavior:

- identify all descendants;
- downgrade them;
- stop using invalidated claims for control;
- schedule the smallest useful revalidation set.

A system that continues acting on invalidated descendants fails this experiment.

### 3. Partial dependency failure

Create a claim that depends on two independent proofs:

\[
P_3 = f(P_1,P_2)
\]

Falsify only `P_1`.

The system should preserve `P_2` and only invalidate the portion of the scientific state that actually depends on `P_1`.

This tests whether provenance is granular rather than all-or-nothing.

### 4. Independent external proof

Give a downstream claim both a chain-derived proof and an independent validation.

If the chain-derived ancestor later fails, the independently supported claim may remain valid if the independent evidence is sufficient.

This prevents excessive invalidation.

### 5. Regime shift

Let the original proofs be valid under environment `E_0`, then change to `E_1` outside their applicability bounds.

The system should mark the affected proofs as `STALE` rather than `FALSIFIED` when appropriate.

This distinguishes:

- wrong claim;
- expired scope;
- missing identifiability;
- true contradiction.

### 6. False-but-useful shortcut

Introduce a model that predicts short-term control correctly for the wrong causal reason.

The system should detect that predictive success alone is not equivalent to causal validity when intervention evidence contradicts the stated mechanism.

## Baselines

Compare against:

1. no provenance memory;
2. scalar confidence only;
3. append-only evidence log without dependency edges;
4. proof graph without invalidation propagation;
5. full proof-chained controller.

## Metrics

### Scientific integrity

- invalid descendants detected;
- false descendants left active;
- over-invalidation rate;
- revalidation precision;
- causal claim survival under falsification.

### Efficiency

- experiments required per validated claim;
- redundant rechecks avoided;
- revalidation cost after failure;
- trust cost across the chain;
- control cost before and after proof reuse.

### Recovery

- time/steps to recover after upstream falsification;
- fraction of valid knowledge preserved;
- fraction of invalid knowledge removed;
- downstream control failures avoided.

## Trust-cost model

One bounded synthetic metric:

\[
TrustCost(c)=ValidationCost(c)+DependencyRisk(c)+StalenessRisk(c)
\]

A valid reusable proof may lower validation cost:

\[
ValidationCost_{next} \downarrow
\]

but invalidation or scope drift should increase trust cost again:

\[
Falsification \lor ScopeDrift \Rightarrow TrustCost \uparrow
\]

## Evidence packet

Every proof node should be replayable from a compact evidence packet containing at minimum:

```text
proof_id
claim
upstream_proof_ids
model_version
experiment_config
random_seed_or_determinism_record
prediction
falsification_condition
observation
evidence_hashes
applicability_bounds
status
```

## Critical negative results

The experiment should explicitly permit results such as:

- `PROOF_REUSE_PROVIDES_NO_EFFICIENCY_GAIN`
- `INVALIDATION_PROPAGATION_TOO_BROAD`
- `INVALIDATION_PROPAGATION_MISSES_DESCENDANTS`
- `INDEPENDENT_REVALIDATION_REQUIRED_TOO_OFTEN`
- `SCALAR_CONFIDENCE_MATCHES_PROOF_GRAPH`
- `CHAIN_ERROR_AMPLIFIES_DOWNSTREAM`
- `MODEL_CLASS_INADEQUATE`
- `NON_IDENTIFIABLE_UNDER_CURRENT_INTERVENTIONS`

A negative result is informative and must not be reframed as success.

## Falsification criterion

The central hypothesis is weakened if the full proof-chain system cannot outperform simpler provenance baselines on both:

1. downstream error containment after an upstream failure; and
2. reduction of redundant validation when the chain remains valid.

If it only improves one of these, the result is mixed rather than a general success.

## Interpretation boundary

This experiment concerns a synthetic, auditable scientific-control workflow.

It does **not** demonstrate:

- autonomous real-world laboratory science;
- physical material discovery without calibration;
- universal causal laws;
- independent scientific agency;
- physical proof beyond the evidence actually produced.

Any real-world claim requires calibrated experiments and independent external replication.

## Relation to previous experiments

Experiment 053 chooses experiments by information gain and falsification value.

Experiment 054 switches between discovery and control.

Experiment 055 makes each control action carry its own proof packet.

Experiment 056 adds long-horizon proof dependency, invalidation propagation, and selective revalidation.

The combined loop is:

\[
Hypothesis \rightarrow Experiment \rightarrow Proof \rightarrow Decision \rightarrow New\ Proof
\]

with the additional invariant:

\[
No\ downstream\ trust\ without\ valid\ upstream\ provenance.
\]

## Next experiment

**Experiment 057 — Minimal Revalidation / Proof Repair**

Given a broken proof graph, find the smallest set of new experiments needed to restore trustworthy downstream conclusions:

\[
R^*=\arg\min_R Cost(R)
\]

subject to restoring sufficient evidential support for the target claims.

This turns proof recovery into an optimization problem rather than rerunning the entire scientific history.
