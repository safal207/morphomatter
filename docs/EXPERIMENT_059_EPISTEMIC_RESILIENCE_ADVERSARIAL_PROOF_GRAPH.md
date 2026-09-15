# Experiment 059 — Epistemic Resilience / Adversarial Proof Graph

## Goal

Test whether the MorphoMatter proof architecture can distinguish genuinely independent evidence from multiple apparently separate proofs that share hidden failure modes.

The central question is:

> Can the system resist false confidence when many proofs agree only because they are correlated, duplicated, stale, confounded, or derived from the same hidden source?

The key distinction is:

\[
Many\ proofs \neq Independent\ proofs
\]

and therefore:

\[
Trust \not\propto RawProofCount
\]

without accounting for provenance and dependence.

## Why this follows Experiment 058

Experiment 058 introduced proof portfolio optimization and rewarded evidence diversity, future trust savings, and repair value.

That creates a new failure mode:

> a portfolio may appear diversified while its members secretly share the same underlying assumption, simulator bug, sensor bias, data source, initialization, or transformation pipeline.

Experiment 059 deliberately injects these failures and tests whether the proof graph detects them before confidence propagates downstream.

## Core hypothesis

A proof graph that tracks only claims and outcomes will overestimate confidence under correlated evidence.

A proof graph that also tracks provenance, mechanism, transformation lineage, measurement channel, initialization, model family, and shared assumptions should better estimate effective evidence diversity.

Define a raw proof set:

\[
P=\{p_1,p_2,...,p_n\}
\]

and a dependency matrix:

\[
D_{ij}\in[0,1]
\]

where `D_ij` estimates how strongly proofs `p_i` and `p_j` share a failure mechanism.

Then define an effective evidence count conceptually as:

\[
N_{eff}(P) < |P|
\]

whenever evidence is strongly correlated.

No single formula is assumed universal; the experiment compares multiple bounded synthetic estimators.

## Architecture

```text
Candidate claim
     ↓
Raw proof set
     ↓
Provenance graph
     ↓
Shared-source / shared-assumption analysis
     ↓
Dependency estimate
     ↓
Correlation-adjusted confidence
     ↓
Adversarial challenge
     ↓
Independent revalidation
     ↓
Updated proof status
```

## Proof provenance dimensions

Each proof should record at least:

- experiment ID;
- raw data source;
- simulator version / code commit;
- model family;
- random seed family;
- initialization procedure;
- measurement channel;
- preprocessing pipeline;
- feature extraction path;
- causal assumptions;
- boundary conditions;
- calibration source;
- operator / controller policy;
- parent proofs;
- transformation lineage;
- timestamp / regime validity window.

The purpose is not bureaucracy. It is to reveal hidden epistemic coupling.

## Adversarial proof families

### A. Duplicate evidence disguised as replication

Create several proofs from the same underlying run but with different summaries or visualizations.

Example:

```text
run_17
 ├─ metric_table
 ├─ phase_plot
 ├─ causal_summary
 └─ stability_score
```

These are multiple artifacts, not multiple independent experiments.

Expected behavior:

```text
ARTIFACT_MULTIPLICITY_NOT_COUNTED_AS_REPLICATION
```

### B. Shared simulator bug

Generate several experiments using different seeds and tasks, but all depend on the same incorrect transition implementation.

The evidence appears reproducible until one independently implemented simulator is introduced.

Expected behavior:

- confidence should be reduced because implementation lineage is shared;
- independent implementation should have disproportionate value;
- if the bug is confirmed, downstream proofs depending on the simulator become `STALE` or `FALSIFIED` according to semantics.

### C. Shared measurement bias

Two or more sensors appear independent but share the same calibration error.

Example:

```text
sensor_A ─┐
          ├─ shared calibration reference → biased estimate
sensor_B ─┘
```

The proof graph should not treat them as fully independent.

### D. Hidden common data source

Different analyses are built from datasets that ultimately originate from one source.

The system should detect that apparent cross-dataset confirmation has less independence than expected.

### E. Stale evidence after regime shift

Proofs valid under environment `E0` are reused after the system changes to `E1`.

The graph must distinguish:

- still valid;
- stale / requires revalidation;
- directly falsified.

### F. Correlated initialization

Several simulations use different nominal seeds but the same constrained initialization manifold.

Results may look robust while never probing other basins of attraction.

### G. Shared model-family blind spot

Different learned models agree because they belong to the same model class and therefore miss the same hidden mechanism.

Introduce a structurally different model family or intervention to test whether the agreement survives.

### H. Leakage through preprocessing

A downstream label, future-state feature, or post-transition statistic is accidentally embedded in the proof-generating pipeline.

The system should downgrade all proofs sharing that preprocessing lineage.

### I. Confounded interventions

Interventions intended to change `X` also systematically change hidden variable `Z`.

Observed agreement across repeated experiments should not automatically establish:

\[
do(X)\rightarrow Y
\]

if `Z` is not separated.

### J. False independence by packaging

The same underlying causal mechanism is expressed through different file names, agents, pipelines, or reports.

Independence must be based on provenance and mechanism, not artifact identity.

## Experimental setup

Construct a synthetic proof graph containing:

- true independent proofs;
- exact duplicates;
- partially dependent proofs;
- hidden common-source proofs;
- stale proofs;
- confounded proofs;
- proofs generated by one flawed simulator;
- proofs generated by a second independent implementation;
- downstream claims with mixed dependency structures.

The evaluator knows the planted ground-truth dependency structure, but the tested proof system does not.

## Competing trust strategies

Compare:

1. **Raw count** — trust increases with number of supporting proofs.
2. **Naive weighted count** — weights proofs by quality but ignores dependence.
3. **Provenance overlap penalty** — discounts shared provenance.
4. **Mechanism diversity score** — rewards distinct causal / measurement paths.
5. **Graph dependency model** — estimates correlated failure through shared ancestors.
6. **Adversarially calibrated trust model** — learns from injected correlated failures.
7. **Oracle dependency model** — synthetic upper bound only.

## Correlation-adjusted trust

A bounded conceptual objective is:

\[
T(C)=Support(C)-DependencyPenalty(C)-StalenessPenalty(C)-ConfounderRisk(C)
\]

where `Support(C)` summarizes valid evidence for claim `C`.

A more structural view is:

\[
T(C)\propto IndependentPathMass(C)
\]

rather than proof count.

No claim is made that one formula is universally correct.

## Effective evidence diversity

Define diversity across several axes:

- source diversity;
- mechanism diversity;
- implementation diversity;
- measurement diversity;
- initialization diversity;
- scale diversity;
- environment diversity;
- causal-intervention diversity.

Two proofs may be independent on one axis but coupled on another.

Therefore diversity should be represented as a vector rather than a single label when possible.

## Adversarial challenge protocol

For each target claim:

1. build an apparently strong portfolio;
2. hide one or more shared dependencies;
3. let the trust model estimate confidence;
4. reveal or perturb the shared dependency;
5. observe invalidation propagation;
6. introduce one truly independent proof;
7. measure whether confidence recalibrates correctly.

## Catastrophic correlation test

Construct a claim supported by many proofs that all share one hidden ancestor:

```text
          hidden ancestor H
          /   /   |   \   \
        P1  P2   P3   P4  P5
          \   \   |   /   /
              Claim C
```

If `H` fails, the proof system should recognize that effective support collapses sharply.

A naive system may incorrectly retain high confidence because `P1...P5` still exist as separate records.

## Independent rescue test

Add one proof `Q` with genuinely separate provenance:

```text
          H
      / / | \ \
    P1 P2 P3 P4 P5
       \  |  /
        Claim C
           ↑
           Q
```

After `H` fails, `Q` should preserve only the portion of claim validity that it actually supports.

This tests granular revalidation and non-binary trust repair.

## Metrics

### 1. False confirmation rate

Fraction of false or unsupported claims incorrectly classified as strongly supported because of correlated evidence.

### 2. Effective diversity estimation error

Difference between estimated and planted independent evidence diversity.

### 3. Correlated-failure detection rate

How often the system identifies hidden common failure modes before downstream damage.

### 4. Calibration under dependence

Does predicted confidence match observed claim reliability as correlation increases?

### 5. Invalidation precision

Fraction of invalidated downstream claims that truly depended on the failed source.

### 6. Invalidation recall

Fraction of affected downstream claims correctly marked for revalidation.

### 7. Independent rescue precision

Does an independent proof preserve only the claims it genuinely supports?

### 8. Repair cost after correlated failure

Cost required to restore valid confidence after a common ancestor fails.

### 9. Invalid-trust leakage

Fraction of decisions or claims that continue using evidence known to be stale, falsified, or dependency-compromised.

Target:

```text
invalid_trust_leakage = 0
```

### 10. Proof concentration risk

Fraction of total downstream authority that depends on the most central epistemic ancestor.

## Baseline outcomes

Possible positive bounded result:

```text
PROVENANCE_AWARE_TRUST_RESISTS_CORRELATED_CONFIRMATION
```

Possible mixed result:

```text
DEPENDENCY_DETECTION_IMPROVES_SAFETY_BUT_OVER_DISCOUNTS_VALID_REPLICATION
```

Possible null / negative results:

```text
PROVENANCE_MODEL_NO_BETTER_THAN_NAIVE_WEIGHTING
```

```text
CORRELATION_STRUCTURE_NOT_IDENTIFIABLE_FROM_AVAILABLE_METADATA
```

```text
DIVERSITY_SCORE_FAILS_TO_PREDICT_CORRELATED_FAILURE
```

```text
INDEPENDENT_REPLICATION_TOO_COSTLY_FOR_OBSERVED_GAIN
```

```text
FALSE_INDEPENDENCE_REMAINS_UNDETECTED
```

```text
DEPENDENCY_PENALTY_CAUSES_EXCESSIVE_FALSE_NEGATIVES
```

```text
MODEL_CLASS_INADEQUATE_FOR_EPISTEMIC_DEPENDENCE
```

Negative results must remain negative results.

## Falsification criteria

The central hypothesis is weakened or rejected if:

- provenance-aware scoring does not reduce false confirmation;
- hidden common-source failures remain undetected at the same rate as naive counting;
- independent replication provides no measurable calibration benefit;
- dependency penalties mainly suppress true independent evidence;
- adversarial proof portfolios still create persistent invalid-trust leakage.

## Evidence packet

Each proof should emit a replayable record:

```text
proof_id
claim_ids
raw_source_ids
parent_proof_ids
code_commit
simulator_family
model_family
measurement_channel
calibration_source
initialization_family
preprocessing_hash
causal_assumptions
environment_signature
time_validity_window
shared_dependency_candidates
estimated_independence_vector
status
```

Each trust update should record:

```text
claim_id
raw_support_count
effective_support_estimate
identified_shared_dependencies
confidence_before
confidence_after
reason_for_update
revalidation_required
```

## Relation to Experiments 055–058

Experiment 055:

> every action carries a proof packet.

Experiment 056:

> proofs form dependency chains and invalidation propagates.

Experiment 057:

> broken proof graphs are repaired with minimal revalidation.

Experiment 058:

> proofs are selected as a portfolio based on future value.

Experiment 059 adds:

> proof portfolios must be evaluated for hidden dependence, because apparent diversity can be fake.

## MorphoMatter trust principle

The original principle remains:

> Every external proof reduces the cost of the next unit of trust.

Experiment 059 adds a necessary correction:

> Only genuinely independent or correctly dependency-accounted proof should reduce trust cost as if it were new evidence.

Or compactly:

\[
TrustSavings \propto NewIndependentEvidence
\]

not:

\[
TrustSavings \propto NumberOfArtifacts
\]

## Claim boundary

This is a synthetic epistemic-resilience experiment inside the MorphoMatter research framework.

It does **not** establish:

- universal statistical independence criteria;
- real laboratory replication guarantees;
- autonomous detection of every confounder;
- physical validation of a new material law;
- infallible scientific truth tracking.

Physical claims still require calibrated experiments, independent implementation, external measurement, and independent replication.

## Next experiment

### Experiment 060 — Independent Replication Allocation / Proof Decorrelation

Instead of only detecting correlated evidence after it appears, actively choose the next experiment to maximize **epistemic independence** from the current proof portfolio.

Candidate objective:

\[
e^*=\arg\max_e
\frac{ExpectedIndependentEvidenceGain(e)+FailureModeCoverage(e)}{Cost(e)}
\]

Question:

> Can the system deliberately select replications that break shared failure modes rather than merely repeat the same experiment more times?

This turns independence from a passive metric into an active experiment-design target.
