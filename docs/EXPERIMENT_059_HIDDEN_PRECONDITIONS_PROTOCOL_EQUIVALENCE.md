# Experiment 059 — Hidden Preconditions & Protocol Equivalence

## Motivation

A visible procedure is not necessarily the full causal protocol.

Two runs may receive the same commands and still produce different outcomes because their hidden state, preparation history, ordering, dwell times, surfaces, defects, gradients, or prior phase differ.

A useful literary analogy is the finale of *The Little Humpbacked Horse*: copying the visible sequence is not sufficient when the relevant preconditioning differs. The analogy is only conceptual; this experiment is defined entirely in synthetic, testable terms.

## Core hypothesis

Protocol equivalence must include causal preconditions, not only visible actions.

\[
Outcome = F(S_0, H, P, U_{0:T}, E, I, X)
\]

where:

- \(S_0\): initial material state;
- \(H\): state history;
- \(P\): preconditioning;
- \(U_{0:T}\): visible intervention sequence;
- \(E\): environment;
- \(I\): interface state;
- \(X\): hidden or latent factors represented by the synthetic model.

The key claim to test is:

\[
U^{(a)}_{0:T}=U^{(b)}_{0:T}
\not\Rightarrow
Outcome_a = Outcome_b
\]

when causally relevant preconditions differ.

## Research questions

1. Which preconditions materially change the result under an identical visible protocol?
2. Can a controller distinguish protocol identity from causal-state equivalence?
3. Which historical variables are sufficient to predict replication success?
4. Can the system discover missing preconditions from failed replications?
5. How much of the preparation history can be compressed without losing outcome predictability?

## Synthetic factors

Use a controlled state vector that can vary independently:

- previous phase;
- prior field exposure;
- ramp rate;
- dwell duration;
- interface affinity;
- defect density;
- local gradient history;
- ordering of preparation steps;
- damage/recovery history;
- elapsed relaxation time.

The experiment must not map these synthetic variables directly onto a real material without calibration.

## Experimental design

### Phase A — Same visible protocol, different hidden state

Freeze one visible intervention sequence \(U_{0:T}\).

Generate matched pairs that differ in exactly one precondition at a time.

Measure:

- final state;
- attractor reached;
- transition time;
- transition success probability;
- intervention cost;
- prediction error.

### Phase B — Protocol-equivalence classifier

Train or construct a model that receives two candidate runs and predicts whether they are causally equivalent for the target outcome.

Compare representations:

1. visible actions only;
2. visible actions + current snapshot;
3. visible actions + compact history summary;
4. visible actions + full preregistered causal precondition state.

### Phase C — Failed-replication diagnosis

Create a reference successful run.

Then hide one causally relevant preparation variable from the replay description.

Ask the discovery loop to identify the minimal missing variable or intervention required to restore replication.

### Phase D — History compression

Find the smallest sufficient preparation-state representation \(Z_H\) such that:

\[
P(Outcome \mid U, Z_H)
\approx
P(Outcome \mid U, H_{full})
\]

This tests whether the entire history must be replayed or whether a compact causal state is sufficient.

## Baselines

- action-sequence equality only;
- final pre-run snapshot only;
- random history features;
- full-history oracle;
- compact learned causal-state representation.

## Metrics

- replication success rate;
- false-equivalence rate;
- false-inequivalence rate;
- outcome prediction error;
- hidden-precondition discovery accuracy;
- minimum repair cost;
- history compression ratio;
- invalid-trust leakage;
- replay reduction relative to full-history replay.

## Falsification criteria

The hypothesis is weakened if:

- hidden preconditions do not change outcomes in the preregistered synthetic regime;
- current-state snapshots predict outcomes as well as the full causal-history representation;
- failed replication cannot be improved by discovering missing preconditions;
- the proposed causal-state representation offers no gain over action equality.

Negative outcomes must be reported directly.

Suggested status labels:

- `VISIBLE_PROTOCOL_SUFFICIENT_IN_TESTED_REGIME`
- `HIDDEN_PRECONDITIONS_CHANGE_OUTCOME`
- `CURRENT_SNAPSHOT_SUFFICIENT`
- `HISTORY_REQUIRED_FOR_PROTOCOL_EQUIVALENCE`
- `MISSING_PRECONDITION_NOT_IDENTIFIABLE`

## Proof-carrying replication

A replay package should contain:

```text
visible protocol
+ initial-state fingerprint
+ relevant history summary
+ preconditioning record
+ environment/interface state
+ expected outcome
+ falsification condition
+ evidence references
```

A run is not declared equivalent merely because its action list matches.

## Connection to Proof-Chained Control

This experiment extends the proof packet from:

\[
Action + Reason + Prediction + Evidence
\]

to:

\[
Action + Preconditions + History + Reason + Prediction + Evidence
\]

This directly supports the principle:

> Each external proof reduces the cost of the next trust decision only when the causal preconditions that make the proof relevant are themselves preserved or revalidated.

## Scientific boundary

This is a synthetic causal-replication experiment.

It does not claim that a literary work encodes physical science, nor that any specific physical material has the listed hidden variables in the same form. The story is used only as an analogy for the engineering failure mode of copying visible procedures without reproducing causally relevant state.

## Next experiment

Experiment 060 — Causal State Fingerprint & Replication Passport

Goal: construct a minimal, portable state fingerprint that determines whether an external lab or simulator is actually reproducing the same causal starting conditions before attempting a protocol.
