# Experiment 052 — Predictive Control / Dreamed Interventions

## Status

Research roadmap / synthetic experiment design.

This document proposes a bounded simulation study. It does **not** claim physical control of real materials, real energy savings, or validated laboratory behavior.

## Goal

Test whether a learned predictive material-state model can evaluate multiple candidate interventions internally before applying one to the simulated system, and whether this reduces intervention cost while preserving target-state reachability and recovery robustness.

The key shift is:

```text
react after observing the state
        ↓
predict candidate futures
        ↓
choose the smallest useful intervention
        ↓
apply once
        ↓
compare prediction with evidence
```

## Core hypothesis

Given a predictive latent state

\[
Z_t = E(X_{\le t})
\]

and a learned transition model

\[
\hat Z_{t+1:t+h} = F(Z_t, U_{t:t+h-1}, E_t),
\]

we can evaluate candidate interventions

\[
U^{(1)},U^{(2)},\ldots,U^{(n)}
\]

inside the model before acting.

The selected intervention is

\[
U^* = \arg\min_U
\Big[
D(\hat Z_{t+h}(U), Z_{target})
+ \lambda C(U)
+ \beta R(U)
\Big]
\]

where:

- \(D\) = distance from the desired attractor/state;
- \(C(U)\) = intervention cost;
- \(R(U)\) = predicted risk or uncertainty penalty;
- \(\lambda,\beta\) = preregistered weights.

The model is therefore not asked to issue particle-level commands. It searches over **conditions** that reshape the transition landscape.

## Research question

Can internal predictive rollouts improve control compared with reactive or brute-force intervention under the same bounded action envelope?

More specifically:

1. Can the world model reject interventions that look promising locally but lead to bad attractors later?
2. Can it select weaker interventions that reach the same target?
3. Can it predict when no intervention inside the allowed envelope is likely to work?
4. Can it recover after damage by imagining multiple repair trajectories before acting?
5. Does performance collapse when the predictive model is wrong, memory is removed, or counterfactual action dependence is shuffled?

## Architecture

```text
Observed material state X_t
        ↓
Predictive state encoder E
        ↓
Latent material state Z_t
        ↓
Candidate intervention generator
        ↓
World-model rollouts
  do(U1) do(U2) ... do(Un)
        ↓
Predicted futures + uncertainty
        ↓
Cost / target / risk scoring
        ↓
Select U*
        ↓
Apply to simulator
        ↓
Observe real synthetic outcome
        ↓
Prediction error / causal update
```

## Intervention vocabulary

Keep the action space bounded and interpretable. Candidate controls may include synthetic changes to:

- external field amplitude;
- field gradient;
- coupling strength;
- threshold-like transition conditions;
- local source placement;
- environment-like screening parameter;
- interface-affinity parameter;
- duration / dwell time;
- pause / hold / release actions.

No direct command such as "move particle 17 to coordinate x" is allowed.

## Dreamed intervention protocol

For each decision point:

1. Freeze the current state \(X_t\).
2. Encode \(Z_t\).
3. Generate a fixed candidate set or bounded optimizer proposals.
4. Roll every candidate through the same world model and horizon.
5. Record predicted trajectory, uncertainty, attractor probability, and intervention cost.
6. Select one action according to the preregistered objective.
7. Apply only that action to the simulator.
8. Compare predicted and realized transition.
9. Append the result to an immutable evidence trace.

The system must not silently rewrite failed rollouts after observing the outcome.

## Baselines

Compare against:

### B0 — No intervention

Observe natural dynamics only.

### B1 — Reactive controller

Choose the next action from the current observed state without internal rollouts.

### B2 — Fixed cooperative schedule

Reuse a fixed hand-designed policy.

### B3 — Brute-force high-intensity controller

Use a strong intervention envelope intended to maximize short-horizon reachability.

### B4 — Random bounded control

Sample interventions from the same legal action envelope.

### B5 — Oracle-model planner

Use the frozen simulator law directly when available. This is a privileged upper-bound comparator, not a deployable method.

## Required ablations

### A1 — No memory

Replace \(Z_t\) with a current-state-only representation.

### A2 — No action-conditioned prediction

Predict future state without conditioning on \(U\).

### A3 — Shuffled action labels

Randomly permute intervention identities during rollout scoring.

### A4 — Linearized dynamics

Replace the predictive model with a matched linear model.

### A5 — Topology shuffle

Destroy spatial/interaction topology while preserving marginal state statistics.

### A6 — Uncertainty disabled

Choose actions only by predicted target distance and cost.

### A7 — Short-horizon planner

Use horizon 1 while keeping the same candidate set.

These ablations test whether any gain actually depends on predictive causal structure rather than an easier proxy.

## Test regimes

### Regime R1 — Nominal transition

Move from disordered/metastable state to an ordered target.

### Regime R2 — Competing attractors

Provide at least two stable end states so locally attractive actions can lead to the wrong basin.

### Regime R3 — Damage and repair

Damage an already organized structure and test model-based recovery.

### Regime R4 — History dependence

Use matched current observations produced by different prior trajectories.

### Regime R5 — Environment shift

Change a bounded environment parameter after training to test extrapolation.

### Regime R6 — Unreachable target

Construct cases where the target is not reachable inside the legal intervention envelope. A good controller should sometimes abstain rather than fabricate confidence.

## Metrics

Primary metrics:

- target success rate;
- cumulative intervention cost;
- time-to-target;
- post-control stability after control is removed;
- recovery success after damage;
- prediction error over rollout horizon;
- calibration of predictive uncertainty;
- rate of correct abstention in unreachable cases.

Derived metric:

\[
ControlEfficiency =
\frac{TargetSuccess \times Stability}
{InterventionCost + \epsilon}
\]

Report this only alongside the raw components; do not use it to hide trade-offs.

## Counterfactual criterion

A candidate world model is useful for control only if its predictions change correctly under interventions.

For matched starting states:

\[
\hat P(S_{t+h}\mid do(U_a))
\neq
\hat P(S_{t+h}\mid do(U_b))
\]

when the simulator actually produces different outcomes under \(U_a\) and \(U_b\).

The minimum acceptable evidence is therefore intervention-sensitive prediction, not mere next-state forecasting.

## Causal trace

Every executed decision should emit a compact proof record:

```text
state_hash
model_version
candidate_interventions
predicted_outcomes
predicted_uncertainty
selected_intervention
selection_score
realized_outcome
prediction_error
next_state_hash
```

This preserves the MorphoMatter principle:

> every external proof reduces the cost of the next trust decision.

## Falsification conditions

The hypothesis is weakened or rejected if:

- predictive control does not beat reactive control on matched action budgets;
- gains disappear under action-label shuffling;
- multi-step rollouts do not outperform horizon-1 planning in competing-attractor cases;
- uncertainty is uncorrelated with rollout failure;
- the controller acts confidently on unreachable targets;
- lower intervention cost is achieved only by accepting worse success or stability;
- privileged oracle planning is required for every apparent gain.

Negative results are valid outcomes.

## Strong success criterion

A meaningful positive result requires all of the following on held-out synthetic cases:

1. equal or better target success than the reactive baseline;
2. lower median cumulative intervention cost;
3. better competing-attractor avoidance than horizon-1 planning;
4. preserved or improved post-control stability;
5. useful uncertainty calibration;
6. correct abstention on a preregistered subset of unreachable targets;
7. degradation under causal/predictive ablations in the expected direction.

## Interpretation boundary

A positive result would support only this claim:

> Within the frozen synthetic MorphoMatter environment, an action-conditioned predictive state model can improve bounded intervention planning relative to specified baselines.

It would **not** establish:

- physical material intelligence;
- laboratory-valid self-programming matter;
- universal control laws;
- real-world energy efficiency;
- autonomous discovery of new physical laws.

Those claims require independent physical measurement and replication.

## Relation to previous experiments

Experiment 049 asked which mechanisms provide reservoir-like computation.

Experiment 050 asked whether reusable representations emerge without a task-specific objective.

Experiment 051 asked whether those representations predict future material state.

Experiment 052 closes the next loop:

```text
representation
    ↓
prediction
    ↓
counterfactual rollout
    ↓
intervention choice
    ↓
material response
    ↓
evidence
```

This is the first roadmap stage where the learned internal model is evaluated directly by the quality of decisions made from its predicted futures.

## Next experiment

### Experiment 053 — Causal Model-Predictive Experiment Design

Instead of choosing interventions only to reach a target state, choose some interventions because they maximally reduce uncertainty about the transition law itself:

\[
U^* = \arg\max_U
\frac{ExpectedInformationGain(U)}{Cost(U)}
\]

This would connect predictive control back to the active scientific-discovery loop: sometimes the best action is not the one that immediately moves the material toward the target, but the one that most cheaply tells us **which causal model is wrong**.
