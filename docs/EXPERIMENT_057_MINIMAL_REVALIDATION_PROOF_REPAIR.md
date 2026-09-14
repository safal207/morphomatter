# Experiment 057 — Minimal Revalidation / Proof Repair

## Goal

When part of a proof dependency graph becomes stale or falsified, recover trust with the smallest useful set of new experiments instead of replaying the entire scientific history.

## Core hypothesis

If scientific claims are represented as an explicit dependency graph, then proof repair can be formulated as a constrained optimization problem:

\[
R^*=\arg\min_R Cost(R)
\]

subject to restoring the required downstream claims above a predefined trust threshold.

A second form makes the trade-off explicit:

\[
R^*=\arg\max_R \frac{RecoveredTrust(R)}{Cost(R)+\epsilon}
\]

The experiment asks whether targeted revalidation can recover nearly the same validated knowledge as full replay while using substantially fewer interventions.

## Scientific boundary

This is a synthetic proof-management experiment. It does not claim that software trust scores are equivalent to physical truth. A repaired claim is only as strong as the evidence model, intervention coverage, calibration, and external measurements supporting it.

## Representation

Let the proof graph be

\[
G_P=(P,E)
\]

where each node is a claim/proof packet and each directed edge means "depends on".

Each proof node records at least:

- claim;
- evidence references;
- intervention or observation that generated the evidence;
- model/version/environment context;
- confidence or trust state;
- validity scope;
- falsification condition;
- parent dependencies;
- downstream consumers;
- status: VALID, STALE, FALSIFIED, UNKNOWN, or REVALIDATED.

## Failure propagation

If a proof becomes invalid:

\[
Invalidate(P_i) \Rightarrow Reassess(Descendants(P_i))
\]

but descendants are not automatically declared false.

They become unsupported to the degree that they rely on the failed parent. Independent evidence must remain valid.

This distinction is essential:

```text
parent proof fails
      ↓
find affected dependency paths
      ↓
subtract invalid support only
      ↓
preserve independent support
      ↓
identify minimal evidence gaps
```

## Repair problem

For every damaged downstream claim, estimate the evidence deficit needed to restore its required status.

Candidate repair experiments can:

- directly revalidate the failed proof;
- bypass it with an independent proof;
- revalidate a higher-level downstream claim directly;
- split an overly broad claim into narrower supported claims;
- determine that the claim cannot currently be restored.

The planner chooses a set of experiments that covers the critical evidence gaps at minimal total cost.

## Algorithms to compare

### 1. Full replay

Repeat every historical experiment upstream of the target claim.

### 2. Local parent replay

Only rerun the immediately failed proof nodes.

### 3. Greedy coverage repair

At each step choose the experiment with the largest recovered downstream trust per unit cost.

### 4. Graph-aware minimum repair

Optimize over dependency structure, experiment cost, shared evidence, and independent support.

### 5. Information-aware repair

Prefer experiments that both restore proof and discriminate between competing causal explanations.

## Main benchmark

Construct proof graphs with:

- chains;
- forks;
- shared ancestors;
- redundant independent evidence;
- partially overlapping scopes;
- stale measurements;
- one or more falsified nodes.

Then inject controlled failures and compare repair policies.

## Critical scenarios

### A. Single stale ancestor

A foundational calibration expires but its causal mechanism is not contradicted.

Expected behavior: targeted remeasurement may be sufficient.

### B. Falsified ancestor

A previously accepted causal claim is contradicted.

Expected behavior: descendants depending uniquely on it lose support; repair may require alternative causal evidence rather than simple repetition.

### C. Independent redundancy

A descendant has two independent proof paths and one fails.

Expected behavior: trust decreases only according to the lost path; the valid path must be preserved.

### D. Shared repair

One new experiment can revalidate several damaged branches.

Expected behavior: graph-aware repair should outperform isolated node-by-node replay.

### E. Regime shift

Environment changes so old evidence is only partially transferable.

Expected behavior: repair should target changed boundaries, not replay unrelated history.

### F. Irreparable claim

No admissible experiment can restore identifiability under the current intervention envelope.

Expected output:

`CLAIM_NOT_REVALIDATABLE_UNDER_CURRENT_EVIDENCE_ENVELOPE`

## Metrics

### Repair cost

\[
C_R=\sum_{e\in R}Cost(e)
\]

### Recovered trust

Fraction of previously valid downstream claims restored to the required evidence state.

### Replay reduction

\[
RR = 1-\frac{Cost(minimal\ repair)}{Cost(full\ replay)}
\]

### Invalid-trust leakage

Fraction of claims incorrectly left trusted after their only supporting evidence failed.

Target: zero.

### Evidence preservation

Fraction of still-valid independent evidence preserved rather than unnecessarily invalidated.

### Repair latency

Number of experimental steps required before critical claims regain a valid state.

### Scientific compression

How much trusted downstream knowledge is restored per new unit of evidence.

## Falsification criteria

The minimal-repair hypothesis is weakened or rejected if:

- targeted repair costs are not lower than full replay;
- repaired graphs retain unsupported claims;
- graph-aware repair provides no advantage over naive local replay;
- the optimizer systematically chooses cheap but non-discriminating experiments;
- failure propagation destroys valid independent evidence;
- repaired claims fail deterministic replay or external validation.

## Negative result labels

Use explicit outcomes such as:

- `FULL_REPLAY_NOT_BEATEN`
- `REPAIR_CAUSED_INVALID_TRUST_LEAKAGE`
- `INDEPENDENT_EVIDENCE_NOT_PRESERVED`
- `GRAPH_AWARE_REPAIR_NO_ADVANTAGE`
- `CLAIM_NOT_REVALIDATABLE_UNDER_CURRENT_EVIDENCE_ENVELOPE`
- `REPAIR_RESTORED_SOFTWARE_CONSISTENCY_ONLY`

## Proof repair packet

Every repaired claim should produce an auditable packet:

```text
claim_id
failed_dependency
failure_type
affected_paths
preserved_independent_evidence
candidate_repairs
selected_experiments
expected_recovery
observed_results
new_status
remaining_uncertainty
replay_hashes
```

## Relation to the MorphoMatter principle

The principle

> every external proof reduces the cost of the next trust step

needs a symmetric rule:

> when a proof fails, trust should increase in cost only along the dependency paths that actually relied on it.

Experiment 057 tests whether that symmetry can be implemented without either extreme:

- blindly trusting descendants after their evidence fails; or
- discarding the entire accumulated knowledge base after one local failure.

## Success criterion

A successful result would show that graph-aware minimal revalidation restores the required downstream proof state with materially lower intervention cost than full replay, while maintaining zero unsupported-trust leakage and preserving independent valid evidence.

## Next experiment

### Experiment 058 — Value of Proof / Experiment Portfolio Optimization

Once repair is possible, the next question is which new proofs are worth collecting before anything breaks.

Estimate the expected future value of an experiment from:

- immediate scientific information;
- control improvement;
- number of downstream claims it can support;
- redundancy it adds to fragile proof paths;
- expected future revalidation savings.

A possible objective is:

\[
V(e)=InformationGain(e)+ControlValue(e)+FutureTrustSavings(e)-Cost(e)
\]

This turns proof gathering into portfolio design rather than one-step experiment selection.
