# Experiment 054 — Closed-Loop Causal Discovery and Control

## Goal

Test whether a system that alternates between causal discovery and control can reach targets more reliably and with lower cumulative intervention cost than a controller that acts without first reducing model uncertainty.

## Core idea

The controller should not always optimize the same objective.

Sometimes it should exploit its current model to control the material.
Sometimes it should deliberately run an informative experiment because the causal model is too uncertain.

The closed loop is:

\[
observe \rightarrow infer \rightarrow experiment \rightarrow update \rightarrow control \rightarrow detect\ mismatch \rightarrow infer
\]

## Main hypothesis

A bounded amount of causal exploration can reduce the cost and failure rate of later control when model uncertainty is material.

Formally, choose between two modes:

\[
mode_t \in \{DISCOVER, CONTROL\}
\]

with a switching rule driven by uncertainty, predicted control value, intervention cost, and model mismatch.

A generic objective is:

\[
J = TargetLoss + \lambda_u InterventionCost + \lambda_f FailureCost + \lambda_e ExperimentCost
\]

The central question is whether early discovery can reduce total lifetime cost:

\[
J_{discover\rightarrow control} < J_{control\ only}
\]

under a preregistered regime where the initial causal model is incomplete or ambiguous.

## Architecture

```text
Observation
    ↓
Predictive material state Z_t
    ↓
Causal model / hypothesis set
    ↓
Uncertainty + mismatch estimator
    ↓
Mode selector
   ↙        ↘
DISCOVER   CONTROL
   ↓          ↓
Informative   Goal-directed
intervention  intervention
   ↘          ↙
     Material response
            ↓
       Evidence ledger
            ↓
      Model update
            ↓
         repeat
```

## Discovery mode

Discovery mode chooses interventions primarily for causal identification or falsification.

Example objective:

\[
U^*_{discover}=\arg\max_U \frac{ExpectedInformationGain(U)+FalsificationValue(U)}{Cost(U)+\epsilon}
\]

Discovery should prefer interventions that distinguish competing causal models rather than simply move the system toward the current target.

## Control mode

Control mode chooses interventions for target achievement using the current predictive/causal model:

\[
U^*_{control}=\arg\min_U \Big[PredictedTargetLoss(U)+\lambda Cost(U)+\rho Risk(U)\Big]
\]

The planner may use the predictive world model from Experiment 051 and dreamed interventions from Experiment 052.

## Switching rule

A simple preregisterable rule can use four signals:

- posterior causal uncertainty;
- predictive uncertainty;
- recent model residual / mismatch;
- expected value of additional information.

Example:

```text
if model_mismatch > mismatch_threshold:
    DISCOVER
elif expected_information_gain / experiment_cost > discovery_threshold:
    DISCOVER
else:
    CONTROL
```

This is intentionally simpler than a learned meta-controller for the first bounded experiment.

## Experimental conditions

Compare at least the following policies under the same transition law, action envelope, seeds, and budgets:

1. `CONTROL_ONLY`
   - never performs explicit discovery;
   - updates only from incidental control outcomes.

2. `DISCOVER_THEN_CONTROL`
   - fixed preregistered number of discovery steps;
   - then switches permanently to control.

3. `ADAPTIVE_CLOSED_LOOP`
   - switches between discovery and control based on uncertainty/mismatch.

4. `RANDOM_EXPLORATION_CONTROL`
   - spends the same discovery budget on random interventions before control.

5. `ORACLE_MODEL_CONTROL`
   - privileged upper bound using the true transition model where appropriate;
   - not a deployable baseline.

## Benchmark regimes

Use at least three regimes:

### R1 — Correct but uncertain model

The true model is inside the hypothesis class but initially ambiguous.

Expected result: informative interventions should identify it and improve later control.

### R2 — Misspecified model

The true transition law is outside the candidate model class.

Expected result: a good closed loop should detect persistent mismatch rather than converge to false confidence.

Potential verdict:

`MODEL_CLASS_INADEQUATE`

### R3 — Non-identifiable regime

Available interventions cannot distinguish the relevant hypotheses.

The correct result is not forced selection of one model.

Potential verdict:

`NON_IDENTIFIABLE_UNDER_CURRENT_INTERVENTIONS`

## Disturbance / regime-shift test

After successful control, change one bounded part of the synthetic environment or interaction law without informing the controller.

Then test whether:

```text
prediction residual rises
→ mismatch is detected
→ system leaves CONTROL mode
→ targeted discovery is triggered
→ causal model is updated
→ control recovers
```

This is the key test for a real closed scientific loop rather than a one-shot calibration phase.

## Metrics

### Control metrics

- target success rate;
- cumulative intervention effort;
- time/ticks to target;
- failure or trap rate;
- robustness after disturbances.

### Discovery metrics

- information gain per experiment;
- posterior entropy reduction;
- time to falsify wrong models;
- causal edge / mechanism identification accuracy where ground truth exists;
- number of experiments before the useful model is identified.

### Closed-loop metrics

- total lifetime cost;
- number of mode switches;
- regret relative to oracle control;
- recovery cost after regime shift;
- fraction of discovery actions that produce useful model updates;
- calibration of uncertainty versus realized model error.

## Evidence ledger

Every intervention must produce a replayable record:

```text
state_before
candidate_models
posterior_before
mode
selected_intervention
selection_rationale
predicted_outcomes
observed_outcome
prediction_residual
posterior_after
state_after
```

This supports the project principle:

> every external proof reduces the cost of the next trust decision.

The evidence chain should make it possible to verify why the system switched modes and whether the model update was justified by observations.

## Ablations

Run at least:

- no uncertainty estimate;
- no mismatch detector;
- no explicit causal model update;
- no information-gain objective;
- fixed discovery budget only;
- random discovery matched for intervention count and cost;
- no history / hysteresis state;
- shuffled causal topology where applicable.

The purpose is to identify which mechanism is responsible for any closed-loop benefit.

## Strong success criterion

Do not call the experiment successful merely because `ADAPTIVE_CLOSED_LOOP` reaches the target.

A meaningful positive result requires all of the following in at least one preregistered uncertain regime:

1. lower total lifetime cost or higher success than `CONTROL_ONLY`;
2. advantage over cost-matched random exploration;
3. causal/model uncertainty measurably decreases before the control advantage appears;
4. the evidence ledger supports replay of the discovery→update→control chain;
5. under a hidden regime shift, mismatch detection triggers renewed discovery and improves recovery over staying in control mode.

## Important negative results

These are scientifically useful outcomes:

- discovery cost exceeds all later control savings;
- control-only performs equally well;
- uncertainty is poorly calibrated;
- discovery selects interventions that do not distinguish models;
- model mismatch is detected but cannot be resolved;
- the action envelope makes the target unreachable;
- the system cannot identify the true mechanism within the hypothesis class.

Possible verdicts:

- `CLOSED_LOOP_DISCOVERY_REDUCES_CONTROL_COST`
- `DISCOVERY_COST_EXCEEDS_CONTROL_BENEFIT`
- `RANDOM_EXPLORATION_MATCHES_CAUSAL_DISCOVERY`
- `MODEL_CLASS_INADEQUATE`
- `NON_IDENTIFIABLE_UNDER_CURRENT_INTERVENTIONS`
- `TARGET_UNREACHABLE_WITHIN_ACTION_ENVELOPE`

## Scientific boundary

This experiment is a synthetic closed-loop causal-control benchmark.

A positive result would show that, inside the implemented model and action envelope, alternating between information-seeking experiments and goal-directed control improves performance.

It would not demonstrate autonomous physical science, universal causal discovery, a real material recipe, or laboratory self-organization without independent physical calibration and replication.

## Relation to previous experiments

```text
Exp051: predictive material state
        ↓
Exp052: dreamed interventions for control
        ↓
Exp053: causal experiment selection
        ↓
Exp054: adaptive discovery ↔ control loop
```

Experiment 054 therefore turns the previous components into one bounded system that can decide whether the next action should be taken to learn or to control.

## Next research direction

Experiment 055 — Proof-Carrying Material Control

Require every chosen control action to carry a compact causal justification and an explicit evidence chain showing why the intervention is expected to work, what observation would falsify it, and how confidence should change after the result.
