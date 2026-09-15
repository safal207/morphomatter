# Experiment 062 — Federated Claim Consensus Without Majority Voting

## Goal

Define a bounded framework for combining conflicting evidence across multiple labs, agents, pipelines, and trust domains without reducing scientific consensus to a simple majority vote.

The central question is:

> When independent or partially independent sources disagree, can MorphoMatter derive a calibrated claim status from evidence quality, scope match, uncertainty, causal compatibility, and trust-domain independence rather than from the number of agreeing sources?

## Core principle

Scientific agreement is not a vote count.

\[
Consensus(C) \neq MajorityVote(C)
\]

Instead, for a claim `C`:

\[
Consensus(C)=f(I,S,Q,U,K,R)
\]

where:

- `I` = evidence independence;
- `S` = scope match between evidence and claim;
- `Q` = evidence quality;
- `U` = uncertainty and calibration;
- `K` = causal compatibility;
- `R` = replication structure across trust domains.

The framework must be able to conclude that evidence is unresolved, non-identifiable, or scope-dependent rather than forcing a binary verdict.

## Why this extends Experiment 061

Experiment 061 separated internal diversity from external replication and introduced trust-domain vectors.

Experiment 062 asks the next question:

> Given a federation of partially independent and sometimes conflicting proofs, how should a claim be represented without majority voting?

This moves from replication accounting to evidence synthesis.

## Claim object

Each claim should be explicit and bounded:

```text
claim_id
statement
scope
population_or_material_family
environment_range
intervention_range
time_horizon
scale
required_observables
known_exclusions
status
```

A claim with vague scope cannot be meaningfully federated.

## Evidence object

Each evidence packet should expose:

```text
evidence_id
claim_id
result
scope_tested
trust_domain_vector
method
code_version
instrument_or_simulator
calibration_chain
operator_or_agent
initial_conditions
uncertainty
quality_flags
causal_assumptions
raw_or_replayable_artifacts
status
```

## Trust-domain independence

Reuse the trust-domain vector from Experiment 061:

\[
D(p)=\{code,hardware,instrument,calibration,operator,environment,pipeline,evidence\ store\}
\]

Two proofs are not fully independent if important components of `D(p)` overlap.

Define a synthetic independence score:

\[
I(p_i,p_j) \in [0,1]
\]

but do not treat the scalar as ground truth; retain the underlying dependency explanation.

## Scope compatibility

A failed replication outside the original claim scope is not automatically a contradiction.

For evidence `e` and claim `C`, define:

\[
S(e,C)=ScopeMatch(e,C)
\]

with categories such as:

```text
EXACT_SCOPE
STRICT_SUBSET
PARTIAL_OVERLAP
ADJACENT_SCOPE
OUT_OF_SCOPE
UNKNOWN_SCOPE
```

Only evidence with meaningful scope overlap should directly update the claim.

## Evidence quality

Quality should be multidimensional rather than a single opaque reputation score.

Possible dimensions:

- preregistration / frozen protocol;
- deterministic replay availability;
- raw evidence availability;
- calibration traceability;
- protocol completeness;
- negative-control coverage;
- falsification tests;
- model assumptions exposed;
- uncertainty reporting;
- reproducibility by an independent runner.

## Causal compatibility

Two results can disagree at the outcome level while both being valid under different causal regimes.

Example:

```text
Lab A: transition occurs
Lab B: transition does not occur
```

Possible explanations include:

- different hidden state/history;
- different interface condition;
- different environment regime;
- different boundary condition;
- different measurement sensitivity;
- genuine causal-model failure.

The system should therefore test whether disagreement can be explained by an explicit causal separator before declaring a contradiction.

## Consensus states

Do not force `TRUE/FALSE`.

Use bounded statuses such as:

```text
SUPPORTED_WITHIN_SCOPE
SUPPORTED_BUT_DEPENDENCY_LIMITED
MIXED_EVIDENCE
SCOPE_SPLIT
REPLICATION_CONFLICT
NON_IDENTIFIABLE_UNDER_CURRENT_EVIDENCE
FALSIFIED_WITHIN_SCOPE
STALE_AFTER_REGIME_SHIFT
INSUFFICIENT_INDEPENDENT_REPLICATION
```

## Federation architecture

```text
Claim C
  ↓
Collect evidence packets
  ↓
Scope alignment
  ↓
Trust-domain dependency analysis
  ↓
Quality + uncertainty checks
  ↓
Causal compatibility analysis
  ↓
Conflict decomposition
  ↓
Consensus state
  ↓
Recommended discriminating experiment
```

## No majority voting

A synthetic benchmark should include cases where majority vote is intentionally wrong.

### Case A — correlated majority

Nine agreeing internal runs share one simulator bug.

One external replication with independent code disagrees.

A count-based rule produces 9–1 support.

A dependency-aware rule should recognize that effective evidence may be closer to 1–1 than 9–1.

### Case B — scope mismatch

Five external failures test a different environment regime.

Two exact-scope replications succeed.

The system should not treat the five failures as stronger evidence against the original bounded claim.

### Case C — high-quality minority

Several low-quality reports agree, while one high-quality preregistered and replayable independent result contradicts them.

The contradiction should trigger diagnosis, not be drowned by vote count.

### Case D — real heterogeneous effect

Two labs disagree because the effect genuinely changes across regimes.

The correct result is `SCOPE_SPLIT`, not forcing one global claim.

## Consensus computation

A possible bounded synthetic formulation is:

\[
Support(C)=\sum_e w_e \cdot sign(e)
\]

where `w_e` is not a free confidence score but a function of explicit components:

\[
w_e=g(I_e,S_e,Q_e,U_e,K_e)
\]

However, the experiment should compare this scalar aggregation against graph-based evidence reasoning because a single scalar can hide dependencies.

## Evidence graph formulation

Represent the federation as a graph:

```text
Evidence nodes
Claim nodes
Trust-domain nodes
Assumption nodes
Scope nodes
Calibration nodes
```

Edges encode:

```text
SUPPORTS
CONTRADICTS
DEPENDS_ON
SHARES_SOURCE_WITH
VALID_WITHIN
REQUIRES_ASSUMPTION
REPLICATES
INVALIDATES
```

Consensus is then a graph state, not just a score.

## Conflict decomposition

When evidence conflicts, classify the conflict before updating claim status:

```text
DEPENDENCY_CONFLICT
SCOPE_CONFLICT
MEASUREMENT_CONFLICT
CALIBRATION_CONFLICT
CAUSAL_MODEL_CONFLICT
REGIME_SHIFT_CONFLICT
UNEXPLAINED_REPLICATION_CONFLICT
```

This produces a more useful output than `labs disagree`.

## Experiment design

Construct synthetic federations with controlled ground truth and hidden dependency structure.

Vary:

- number of labs;
- number of nominal proofs;
- degree of shared infrastructure;
- scope overlap;
- measurement quality;
- calibration quality;
- uncertainty calibration;
- causal regime variation;
- injected common-mode failures.

Compare:

1. majority vote;
2. naive weighted average;
3. quality-weighted aggregation;
4. independence-adjusted aggregation;
5. graph-based federated consensus;
6. oracle structure-aware benchmark.

The oracle is only an upper bound available in the synthetic setting.

## Metrics

### Consensus calibration

Does reported support correspond to empirical correctness under synthetic ground truth?

### Correlated-majority resistance

How often does the method avoid a wrong conclusion when many agreeing proofs share one hidden failure mode?

### Scope precision

How often does the method avoid applying evidence outside the tested scope?

### Conflict diagnosis accuracy

Can the method distinguish dependency, scope, calibration, causal-model, and genuine replication conflicts?

### Abstention quality

How often does the system correctly return unresolved states instead of forcing a conclusion?

### False-consensus rate

Fraction of cases where the system declares strong support despite insufficient independent evidence.

### False-falsification rate

Fraction of cases where an out-of-scope or correlated failure incorrectly falsifies a valid bounded claim.

### Resolution efficiency

Cost of the next discriminating experiment required to move from conflict to a better-identified claim.

## Discriminating experiment selection

When consensus is unresolved, choose the next experiment to maximally separate competing explanations.

\[
e^*=\arg\max_e \frac{ExpectedConflictReduction(e)}{Cost(e)}
\]

Examples:

- independent reimplementation;
- alternate calibration chain;
- exact-scope replication;
- cross-regime sweep;
- orthogonal observable;
- negative-control experiment;
- intervention that separates two causal models.

## Adversarial scenarios

Test at least:

1. many duplicate proofs disguised as independent labs;
2. independent labs using the same flawed upstream dataset;
3. different instruments sharing one calibration artifact;
4. contradictory evidence caused entirely by scope mismatch;
5. contradiction caused by hidden hysteresis/history;
6. one adversarial or corrupted evidence packet;
7. one highly central proof becoming stale;
8. a true effect that exists only in a narrow regime;
9. a majority of low-quality evidence against a minority of high-quality independent evidence;
10. no available intervention capable of resolving the conflict.

## Required null and negative outcomes

Valid outcomes include:

```text
MAJORITY_VOTE_OUTPERFORMS_UNDER_THIS_SYNTHETIC_REGIME
```

```text
DEPENDENCY_MODEL_MISCLASSIFIES_INDEPENDENCE
```

```text
SCOPE_MODEL_TOO_COARSE_FOR_VALID_FEDERATION
```

```text
GRAPH_CONSENSUS_NO_GAIN_OVER_SIMPLE_WEIGHTING
```

```text
CONFLICT_NOT_RESOLVABLE_WITH_AVAILABLE_EXPERIMENTS
```

```text
EVIDENCE_QUALITY_SCORE_NOT_CALIBRATED
```

Negative results must remain first-class evidence.

## Evidence ledger

Each consensus update should emit:

```text
claim_id
previous_status
evidence_added
evidence_removed_or_staled
scope_alignment_summary
trust_domain_overlap_summary
quality_summary
uncertainty_summary
causal_compatibility_summary
conflict_class
new_status
next_discriminating_experiment
replay_refs
```

## Success criteria

Experiment 062 is positive only if the federated method, under matched evidence and budget:

- lowers false-consensus rate relative to majority vote;
- avoids scope leakage;
- detects correlated evidence clusters;
- preserves explicit uncertainty;
- produces useful conflict classifications;
- selects discriminating experiments that reduce disagreement efficiently;
- maintains `invalid_trust_leakage = 0`.

## Relation to the MorphoMatter proof principle

The existing principle is:

> Every external proof reduces the cost of the next unit of trust.

Experiment 062 refines it:

> External proof reduces trust cost only to the extent that it adds independent, scope-matched, causally interpretable information.

Therefore:

\[
TrustGain \propto NewIndependentInformation
\]

not raw proof count.

## Claim boundary

This is a synthetic evidence-federation framework.

It does **not** establish:

- real scientific consensus across laboratories;
- reliability of any specific institution;
- physical validation of MorphoMatter claims;
- a universal rule for weighting scientific studies.

Those require real external replication, transparent protocols, domain-specific statistical methods, and independent expert review.

## Next experiment

### Experiment 063 — Causal Disagreement Resolution Market

Allocate a fixed experimental budget across competing unresolved claims and disagreements.

Instead of asking only:

> Which claim is most uncertain?

ask:

> Which disagreement is most valuable to resolve next because resolving it unlocks the largest amount of downstream knowledge, control capability, and proof repair?

A candidate objective is:

\[
Priority(d)=\frac{ExpectedUnlockedValue(d)\cdot ConflictSeverity(d)}{ResolutionCost(d)}
\]

This extends proof portfolio optimization from collecting evidence to strategically resolving the most consequential scientific disagreements.
