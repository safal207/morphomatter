# Experiment 061 — Cross-Lab Proof Federation / External Replication Boundary

## Goal

Separate internal diversity from genuinely external replication.

Experiment 060 introduced proof decorrelation inside one research stack. Experiment 061 asks a stricter question:

> Has a result survived a replication attempt across an actually independent trust domain?

The core distinction is:

\[
Internal\ diversity \neq External\ replication
\]

Changing seeds, observables, geometries, or model families can reduce correlation, but evidence may still share hidden infrastructure, assumptions, software, calibration, operators, or storage.

## Core hypothesis

Confidence should increase more when a claim survives replication across independent trust domains than when it is repeated many times inside one domain.

Represent each proof `p` with a trust-domain vector:

\[
D(p)=\{code, hardware, instrument, calibration, operator, environment, pipeline, evidence\ store\}
\]

Two proofs are more independent when fewer critical trust-domain components are shared.

## Trust domains

At minimum, track:

1. **Code domain** — simulator, controller, preprocessing, analysis implementation.
2. **Hardware domain** — compute platform or physical apparatus.
3. **Instrument domain** — sensors and measurement chain.
4. **Calibration domain** — calibration reference, procedure, coefficients, and timestamps.
5. **Operator domain** — person/agent executing and interpreting the experiment.
6. **Environment domain** — lab, chamber, physical setup, or simulation environment.
7. **Pipeline domain** — data ingestion, transformations, filtering, statistics.
8. **Evidence-storage domain** — provenance store, artifact registry, checksums, signatures.
9. **Model-assumption domain** — shared priors, transition law, controller assumptions.
10. **Funding/incentive domain** — optional metadata for correlated procedural bias; not a scientific failure by itself.

The experiment remains synthetic unless real external labs and physical measurements are used.

## Replication classes

Define bounded labels rather than a binary independent/not-independent flag.

### R0 — Same-run restatement

Same underlying evidence, different report or representation.

```text
R0_RESTATEMENT
```

### R1 — Internal rerun

New run, but same code, pipeline, operator, calibration, and evidence store.

```text
R1_INTERNAL_RERUN
```

### R2 — Internally decorrelated replication

Meaningful internal changes such as new seed, observable, geometry, model family, or pipeline branch, but still inside one organizational trust domain.

```text
R2_INTERNAL_DECORRELATED
```

### R3 — Partially external replication

At least one major trust domain is independent, but important infrastructure remains shared.

```text
R3_PARTIAL_EXTERNAL
```

### R4 — Strong external replication

Independent execution with materially separate code/pipeline or independent reimplementation, separate operator, separate evidence store, and—when physical—independent apparatus/calibration chain.

```text
R4_STRONG_EXTERNAL
```

### R5 — Cross-context replication

R4 plus successful replication across a meaningfully different environment, scale, material instance, apparatus, or site.

```text
R5_CROSS_CONTEXT
```

These labels describe evidence independence; they do not guarantee the claim is true.

## Architecture

```text
Claim
  ↓
Existing proof graph
  ↓
Trust-domain decomposition
  ↓
Shared-dependency analysis
  ↓
Replication gap
  ↓
Replication allocator
  ↓
Independent execution domain
  ↓
Signed / replayable evidence packet
  ↓
Federated proof graph
  ↓
Confidence + boundary update
```

## Federation graph

Extend the proof graph so proofs have both scientific dependencies and trust-domain dependencies.

```text
Claim C
  ↑
 ┌───────────────┐
 P_A             P_B
 Lab A           Lab B
 code_A          code_B
 calib_A         calib_B
 store_A         store_B
  └──── no hidden shared critical dependency ────┘
```

A replicated claim should record not only `supports(C)` but also which trust-domain components remain shared.

## Independence score

A simple synthetic score can be used for allocation experiments:

\[
I(p_i,p_j)=1-\frac{\sum_k w_k\,Shared_k(p_i,p_j)}{\sum_k w_k}
\]

where `Shared_k` is 1 when a critical domain is shared and `w_k` is the importance weight of that domain.

This score is only a planning heuristic. It is not a universal scientific measure of independence.

## Effective external replication count

Raw replication count can exaggerate evidence strength.

Define:

\[
N_{external,eff} \leq N_{external,raw}
\]

Correlated replications should contribute less than genuinely independent ones.

A cluster of ten replications using the same library bug may have an effective independence close to one.

## Main experimental design

Create synthetic claims with hidden common-mode failure sources.

For each claim, generate candidate replication sites with known trust-domain overlap.

Compare allocation policies under matched cost:

1. **Repeat-most** — maximize number of reruns.
2. **Cheapest-lab** — choose cheapest available replication.
3. **Seed-diversity** — only vary random seeds.
4. **Internal decorrelation** — optimize Experiment 060 dimensions but remain in one domain.
5. **External-domain diversity** — explicitly minimize critical trust-domain overlap.
6. **Failure-mode targeting** — choose the site most likely to break the dominant common-mode failure.
7. **Proof-federation optimizer** — maximize external information gain, trust-domain diversity, and repair value per cost.
8. **Oracle upper bound** — synthetic benchmark only.

## Adversarial scenarios

### 1. Shared dependency disguised as external replication

Two labs use different wrappers but the same core numerical library with the same bug.

Expected behavior:

```text
EXTERNAL_REPLICATION_DOWNGRADED_SHARED_CORE_DEPENDENCY
```

### 2. Independent code, shared calibration

Different analysis implementations but one common calibration reference is wrong.

### 3. Independent operators, shared dataset

Different teams analyze the same flawed raw dataset.

This is independent analysis, not independent replication.

### 4. Independent evidence store, same apparatus

Checksums and provenance are separate, but the physical measurement chain is common.

### 5. Different apparatus, same preprocessing leak

A central preprocessing package contaminates every result.

### 6. One external failure against many internal successes

The system must not automatically discard the external failure as an outlier.

Expected status:

```text
REPLICATION_CONFLICT_REQUIRES_CAUSAL_DIAGNOSIS
```

### 7. Cross-context success but exact-context failure

A model may transfer to one context while failing its original claim boundary. Do not merge these into one claim.

## Replication conflict handling

When external replication disagrees with the current proof graph:

```text
conflict
  ↓
freeze claim escalation
  ↓
identify trust-domain differences
  ↓
construct discriminating experiments
  ↓
separate claim boundary if needed
  ↓
update / falsify / narrow claim
```

Never resolve conflict by simple majority vote over correlated proofs.

## Claim-boundary tracking

A replicated law should carry an applicability envelope:

\[
Claim = (statement, material, environment, scale, history, apparatus\ assumptions)
\]

External replication may:

- confirm the same boundary;
- narrow the boundary;
- split the claim into regimes;
- falsify the claim;
- remain inconclusive.

## Core metrics

### External independence gain

Increase in effective trust-domain diversity after replication.

### Common-mode failure detection rate

Fraction of injected shared failure modes correctly identified.

### False external-confirmation rate

How often the system labels correlated evidence as independent replication.

Target:

```text
false_external_confirmation_rate → 0
```

### Conflict sensitivity

Probability that one credible independent contradiction triggers re-evaluation rather than being suppressed by many correlated confirmations.

### Reimplementation value

Incremental value of independently reimplementing the key mechanism compared with simply rerunning the original code.

### Cross-context transfer

Fraction of externally replicated claims that survive context change without hidden scope expansion.

### Repair value

How much an external proof path reduces revalidation cost if an internal proof chain later fails.

### Invalid-trust leakage

Use of stale, falsified, or improperly classified replication evidence in downstream control.

Target:

```text
invalid_trust_leakage = 0
```

## Evidence packet

Each external replication should emit a replayable federation record:

```text
replication_id
claim_id
replication_class
site_or_domain_id
code_identity
implementation_independence
hardware_identity
instrument_identity
calibration_chain_id
operator_or_agent_id
environment_id
pipeline_id
evidence_store_id
model_assumption_family
shared_dependencies
known_common_mode_risks
preregistered_prediction
observed_result
uncertainty
raw_evidence_hashes
analysis_hashes
claim_boundary_before
claim_boundary_after
conflict_status
replication_status
```

## Preregistration

Before reading the replication result, freeze:

- target claim;
- exact success/failure criterion;
- intended replication class;
- known shared dependencies;
- analysis plan;
- claim boundary;
- conditions that force downgrade from R4/R5 to a lower replication class.

This reduces post-hoc relabeling of dependence as independence.

## Success criteria

Experiment 061 is positive if trust-domain-aware allocation, under matched cost, achieves several of the following:

- higher common-mode failure detection;
- lower false external-confirmation rate;
- better calibration of claim confidence;
- lower downstream repair cost;
- higher conflict sensitivity;
- no increase in invalid-trust leakage;
- better distinction between reproducibility, independent analysis, replication, and cross-context generalization.

A result that merely produces more replication artifacts is not success.

## Negative and null outcomes

Valid outcomes include:

```text
EXTERNAL_DOMAIN_TRACKING_NO_GAIN_OVER_INTERNAL_DECORRELATION
```

```text
TRUST_DOMAIN_SCORE_POORLY_PREDICTS_FAILURE_INDEPENDENCE
```

```text
INDEPENDENT_REIMPLEMENTATION_TOO_COSTLY_FOR_OBSERVED_GAIN
```

```text
EXTERNAL_REPLICATION_CONFLICT_UNRESOLVED
```

```text
CLAIM_NARROWED_AFTER_EXTERNAL_REPLICATION
```

```text
CLAIM_FALSIFIED_BY_EXTERNAL_REPLICATION
```

```text
REPLICATION_NOT_INDEPENDENT_ENOUGH_FOR_R4
```

```text
CROSS_CONTEXT_GENERALIZATION_NOT_OBSERVED
```

These outcomes must remain negative, mixed, or boundary-narrowing results; they must not be reframed as success.

## Relation to MorphoMatter

MorphoMatter has progressively moved from:

```text
proof
→ proof chain
→ proof repair
→ proof portfolio
→ proof independence
→ external proof federation
```

The project principle becomes stricter:

> Every external proof can reduce the cost of the next unit of trust only to the extent that it contributes genuinely new, independently generated information.

## Claim boundary

This document defines a synthetic research and evidence architecture.

It does **not** claim that MorphoMatter has already been independently replicated by external laboratories.

A real R4/R5 designation requires actual external execution with verifiable independent provenance.

## Next experiment

### Experiment 062 — Federated Claim Consensus Without Majority Voting

Once multiple independent domains disagree, simple vote counting is unsafe because evidence differs in independence, scope, uncertainty, and quality.

The next question is:

> How should MorphoMatter combine conflicting proofs without turning consensus into popularity?

Candidate framing:

\[
Consensus(C) = f(Independence, ScopeMatch, EvidenceQuality, Uncertainty, CausalCompatibility)
\]

rather than:

\[
Consensus(C) = MajorityVote
\]

The goal is a federated scientific consensus mechanism that can preserve disagreement, split claim boundaries, or remain explicitly unresolved.