# Experiment 060 — Independent Replication Allocation / Proof Decorrelation

## Goal

Extend Experiment 059 from detecting correlated evidence to actively allocating new experiments so that confirmation paths become more independent.

The central question is:

> Given an existing proof graph, which next replication most reduces shared failure modes rather than merely adding another artifact that agrees with the same assumptions?

This is a synthetic research-planning framework for MorphoMatter. It does not itself demonstrate real-world physical replication.

## Core principle

Many matching results can still be one effective proof if they share the same hidden source of error.

Therefore the objective is not:

\[
\max \; NumberOfConfirmingRuns
\]

but rather:

\[
\max \; IndependentInformation
\]

under a bounded cost.

A replication candidate `r` should be valued partly by how much it breaks dependence on existing evidence.

Define a bounded synthetic utility:

\[
U(r)=IG(r)+DecorrelationGain(r)+FailureModeCoverage(r)+RepairValue(r)-Cost(r)-Risk(r)
\]

where:

- `IG(r)` is expected information gain;
- `DecorrelationGain(r)` is expected reduction in evidence dependence;
- `FailureModeCoverage(r)` is the number/importance of currently shared failure modes challenged by the replication;
- `RepairValue(r)` is future value if another proof becomes stale or falsified;
- `Cost(r)` is execution cost;
- `Risk(r)` penalizes fragile or poorly identifiable replications.

## What counts as independent?

Independence is not binary. Two replications may differ in one dimension but remain coupled in another.

Represent each proof by a dependence signature:

```text
proof_id
simulator_or_pipeline
model_family
initialization_family
random_seed_family
preprocessing_path
measurement_channel
observable
intervention_family
parameterization
geometry
scale
operator_or_agent
calibration_source
external_dataset_source
code_revision
```

Two proofs are highly correlated if they share many high-risk dimensions.

## Failure-mode graph

Introduce an explicit hidden-failure graph:

```text
Failure mode F1 ──→ Proof P1
                └─→ Proof P2

Failure mode F2 ──→ Proof P2
                └─→ Proof P3
```

Examples of synthetic failure modes:

- same simulator bug;
- same transition law implementation bug;
- same preprocessing leakage;
- same calibration error;
- same biased initialization family;
- same causal model family;
- same hidden confounder;
- same random-number construction;
- same observable blind spot;
- same geometry encoding error;
- same regime assumption.

The purpose of replication allocation is to select experiments that cut these shared dependencies.

## Replication axes

A replication can deliberately differ along one or more axes.

### 1. Seed independence

Use independently generated stochastic seeds.

This is useful only for stochastic uncertainty. It does not protect against deterministic implementation bugs.

### 2. Initialization independence

Use different initial-condition families rather than different samples from the same narrow family.

### 3. Observable independence

Measure the claimed transition through a different observable.

Example:

```text
proof A: ordered-site fraction
proof B: frontier propagation statistic
proof C: attractor membership / recovery outcome
```

Agreement across observables can be stronger than repeated measurement of the same scalar.

### 4. Mechanism independence

Test the same claim using an intervention that acts through a different causal channel.

Example:

```text
environment perturbation
vs.
interface perturbation
vs.
interaction-field perturbation
```

### 5. Model-family independence

Use a structurally different predictor or causal model.

Agreement between two implementations of the same model family should not be treated as fully independent.

### 6. Pipeline independence

Use a separately implemented analysis path.

Where possible, avoid shared preprocessing, helper functions, cached outputs, or common derived artifacts.

### 7. Scale independence

Test whether the claim survives changes in lattice size, temporal horizon, or coarse-graining level.

### 8. Geometry independence

If a conclusion is claimed to be general, replicate it under a different geometry family.

### 9. Regime independence

Test whether the effect survives a different bounded region of the parameter space rather than only rerunning near the original operating point.

## Proof-decorrelation score

For proof `p_i` and candidate replication `r`, define a synthetic dependence score:

\[
D(p_i,r)=\sum_k w_k\,Shared_k(p_i,r)
\]

where `Shared_k` indicates whether a high-risk dependence dimension is shared.

Then define:

\[
DecorrelationGain(r)=\sum_i Authority(p_i)\,[D_{before}(p_i)-D_{after}(p_i,r)]
\]

The exact scoring is a research surrogate, not a universal scientific law.

## Portfolio version

For several replication candidates:

\[
R^*=\arg\max_R
\Big[
JointInformation(R)+JointDecorrelation(R)+RepairCoverage(R)-Cost(R)
\Big]
\]

subject to:

\[
Cost(R)\leq B
\]

This links Experiment 060 directly to Experiment 058's proof-portfolio optimization.

## Experimental setup

Construct a synthetic proof graph where a target claim appears strongly supported by multiple artifacts.

Unknown to the selector, some artifacts share injected hidden failure modes.

Candidate replications are available with different costs and dependence signatures.

The selector must choose which replications to fund.

## Strategies to compare

1. **Repeat-best** — repeat the previously strongest experiment.
2. **Cheapest-repeat** — maximize number of replications under budget.
3. **Random replication** — matched total cost.
4. **Seed-only diversity** — vary seeds but keep pipeline/model fixed.
5. **Observable diversity** — prioritize new measurement channels.
6. **Pipeline diversity** — prioritize independent implementation paths.
7. **Failure-mode-targeted** — choose replications that challenge the most central shared dependencies.
8. **Joint proof-decorrelation policy** — optimize information + independence + repair value.
9. **Oracle benchmark** — synthetic upper bound with access to injected failure-mode identities; never available to practical policies.

## Adversarial scenarios

### Scenario A — Shared simulator bug

Five runs agree, but all use the same faulty transition function.

A new seed should not rescue the claim.

A separate implementation should.

### Scenario B — Shared observable blind spot

Several proofs report the same macroscopic metric while missing a structural defect.

A new observable should expose the inconsistency.

### Scenario C — Shared preprocessing leakage

Multiple downstream analyses appear independent but all consume one contaminated intermediate artifact.

A clean raw-to-result pipeline should break the correlation.

### Scenario D — Regime shift

Old proofs remain internally correct for the old regime but no longer justify current control.

A replication in the new regime should be preferred over another historical-condition replay.

### Scenario E — False diversity

Artifacts differ in filenames, seeds, and reporting agents but still share the same code, calibration, and hidden confounder.

The policy should detect low effective independence.

### Scenario F — Expensive true independence

The only replication that truly breaks the main failure mode is costly.

The system must decide whether the reduction in epistemic risk justifies the cost.

## Metrics

### Effective proof count

Raw proof count is insufficient.

Define an effective count that discounts correlated evidence:

\[
N_{eff}\leq N_{raw}
\]

A strong system should increase `N_eff`, not merely `N_raw`.

### Correlated-failure exposure

Fraction of total claim authority that can fail because of one shared hidden factor.

### Decorrelation gain

Reduction in pairwise or graph-level dependence after selected replications.

### Failure-mode discovery rate

Fraction of injected shared failure modes exposed by the selected replication plan.

### False confirmation rate

How often the system reports stronger confidence despite no real increase in independent information.

### Replication efficiency

\[
ReplicationEfficiency=
\frac{IndependentInformationGain}{Cost}
\]

### Repair value

How much the new independent path reduces future minimal revalidation cost.

### Invalid-trust leakage

Decisions that continue to rely on stale, falsified, or known-correlated evidence.

Target:

```text
invalid_trust_leakage = 0
```

## Success criteria

Experiment 060 is positive only if, under matched budget, the proof-decorrelation policy:

- exposes more correlated failure modes than naive repetition;
- increases effective evidence diversity;
- reduces false confirmation;
- improves resilience when one proof family is invalidated;
- lowers future repair cost or preserves more valid claims;
- does not increase invalid-trust leakage.

A gain only in raw proof count does not count as success.

## Negative and null outcomes

Valid outcomes include:

```text
DECORRELATION_POLICY_NO_GAIN_OVER_RANDOM
```

```text
SEED_DIVERSITY_MISTAKEN_FOR_MECHANISM_DIVERSITY
```

```text
INDEPENDENT_PIPELINE_TOO_COSTLY_FOR_NET_GAIN
```

```text
DEPENDENCE_SIGNATURE_INSUFFICIENT_TO_PREDICT_CORRELATION
```

```text
FALSE_DIVERSITY_NOT_DETECTED
```

```text
REPLICATION_DIVERSITY_REDUCES_STATISTICAL_POWER
```

```text
CLAIM_REMAINS_NON_IDENTIFIABLE_AFTER_REPLICATION
```

These are scientific outcomes, not implementation failures.

## Evidence packet

Each replication decision should emit:

```text
replication_id
parent_claim_id
existing_proof_ids
shared_dependence_signature
candidate_dependence_signature
expected_information_gain
expected_decorrelation_gain
expected_failure_mode_coverage
expected_repair_value
expected_cost
selected_reason
observed_outcome
new_proof_id
dependence_edges_added
dependence_edges_removed_or_weakened
claim_status_before
claim_status_after
actual_decorrelation_gain
actual_repair_value_if_triggered
status
```

## Relation to the project principle

MorphoMatter's principle is:

> Every external proof reduces the cost of the next unit of trust.

Experiment 060 adds a necessary qualification:

> A new proof should reduce trust cost in proportion to the new independent information it contributes, not merely because another artifact agrees.

This protects the project from proof inflation.

## Claim boundary

This experiment defines a synthetic allocation and evidence-graph framework.

It does **not** establish that:

- a physical material law has been independently replicated;
- software-level independence guarantees laboratory independence;
- a numerical decorrelation score is a universal measure of scientific independence;
- MorphoMatter has achieved autonomous real-world scientific validation.

Physical claims still require independently executed, calibrated experiments and external replication.

## Next experiment

### Experiment 061 — Cross-Lab Proof Federation / External Replication Boundary

Move one step beyond internally diversified pipelines.

Represent multiple simulated or eventually real laboratories as separate trust domains with independent:

- codebases;
- instruments;
- calibration chains;
- operators;
- preprocessing;
- priors;
- evidence stores.

Question:

> When does a proof become meaningfully external to the system that generated the original claim?

The key distinction becomes:

\[
Internal\ diversity \neq External\ replication
\]

and the system must track which trust boundaries were actually crossed.
