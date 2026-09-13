# Experiment 053 — Causal Model-Predictive Experiment Design

## Goal

Extend predictive control from choosing interventions that reach a target state to choosing interventions that most efficiently reduce uncertainty about the causal transition model itself.

The experiment asks whether an active learner can select informative interventions that distinguish competing causal explanations faster than passive, random, or target-only control.

## Core hypothesis

Given a set of competing causal models \(M\), choose the next intervention \(U\) by expected information gain per unit cost:

\[
U^*=\arg\max_U \frac{\mathbb{E}[IG(M;Y\mid do(U))]}{Cost(U)+\epsilon}
\]

where:

- \(M\) is uncertainty over candidate causal models;
- \(U\) is a permitted intervention;
- \(Y\) is the resulting observation;
- \(IG\) is expected reduction in model uncertainty;
- \(Cost(U)\) is intervention or experiment cost.

A complementary falsification objective is:

\[
U_{falsify}^*=\arg\max_U \; P(\text{candidate model fails}\mid do(U))
\]

The controller should sometimes prefer an experiment that is not immediately useful for control if it strongly discriminates between competing explanations.

## Architecture

```text
Current observations
        ↓
Predictive material state Z_t
        ↓
Competing causal models {M1, M2, ...}
        ↓
Candidate interventions {U1, U2, ...}
        ↓
Counterfactual rollout under each model
        ↓
Expected information gain / falsification value
        ↓
Cost + safety constraints
        ↓
Execute one bounded intervention
        ↓
Observe evidence
        ↓
Update model posterior / causal graph
        ↓
Repeat
```

## Synthetic benchmark design

Use a family of controlled toy material worlds with partially confounded transition mechanisms. Candidate models should make similar predictions under ordinary trajectories but diverge under specific interventions.

Example competing mechanisms:

1. **Environment-driven nucleation**
   \[
   E_t \rightarrow N_{t+1}
   \]

2. **Interface-mediated nucleation**
   \[
   I_t \rightarrow N_{t+1}
   \]

3. **History-mediated transition**
   \[
   H_t \rightarrow N_{t+1}
   \]

4. **Interaction-field-mediated frontier propagation**
   \[
   \Phi_t \rightarrow F_{t+1}
   \]

Passive observation may leave these explanations observationally similar. Carefully chosen interventions should separate them.

## Intervention vocabulary

Keep the action space bounded and explicit. Example synthetic controls:

- change one environment coordinate;
- perturb interface affinity;
- alter interaction-field amplitude or gradient;
- introduce a localized perturbation;
- vary dwell time or transition rate;
- damage a bounded region and observe recovery;
- hold current conditions constant as a negative-control action.

No action should be interpreted as a physically validated recipe unless calibrated against real measurements.

## Experimental policies to compare

### P0 — Passive observation
No active intervention selection.

### P1 — Random intervention
Sample uniformly from the permitted intervention set.

### P2 — Target-only control
Choose the action expected to move the system toward a desired state, without valuing information gain.

### P3 — Uncertainty sampling
Choose the action where predictive uncertainty is highest.

### P4 — Information-gain planner
Choose the action maximizing expected model discrimination per cost.

### P5 — Falsification-first planner
Choose the action most likely to invalidate the currently leading model.

### P6 — Hybrid scientist-controller
Optimize a weighted objective:

\[
J(U)=\alpha\,ControlUtility(U)+\beta\,InformationGain(U)-\gamma\,Cost(U)-\delta\,Risk(U)
\]

## Primary metrics

- number of experiments needed to identify the correct synthetic mechanism;
- posterior probability assigned to the true model;
- causal edge precision / recall;
- transition prediction error after each experiment;
- cumulative intervention cost;
- falsification efficiency;
- regret relative to an oracle experiment policy;
- calibration of uncertainty;
- transfer to unseen initial states or environment regimes.

## Strong success criterion

A meaningful positive result requires the active causal policy to:

1. identify the correct synthetic mechanism with fewer experiments than random and passive baselines;
2. reduce prediction error on held-out trajectories;
3. survive matched-budget comparisons;
4. retain the advantage across multiple seeds and mechanism families;
5. remain calibrated when none of the candidate causal models is correct.

Success on only one hand-picked mechanism is not sufficient.

## Critical negative controls

### Model-set misspecification
Construct a world where the true mechanism is absent from the candidate model set.

Expected behavior: uncertainty or residual error should remain high rather than forcing false certainty.

### Observationally equivalent models
Include mechanisms that cannot be distinguished under the available intervention set.

Expected behavior: the system should return `NON_IDENTIFIABLE_UNDER_CURRENT_INTERVENTIONS` rather than inventing a winner.

### Shuffled causal labels
Shuffle model identities while preserving predictions. Performance should not depend on labels.

### Randomized outcomes
Destroy the intervention-response relation. Information-gain planning should lose its advantage.

### Cost inversion
Make highly informative actions very expensive. The cost-aware planner should sometimes choose a weaker but cheaper experiment.

### Hidden confounder
Add an unobserved variable affecting both intervention response and transition. The system should show degraded identification and increased uncertainty.

## Falsification rule

A causal claim is strengthened only when an intervention produces evidence that distinguishes it from plausible alternatives.

Observation alone is not enough:

```text
correlation
    ≠
causal identification
```

The target workflow is:

```text
hypothesis
   ↓
prediction under intervention
   ↓
intervention
   ↓
evidence
   ↓
model survives / model fails
```

## Evidence ledger

Every experiment should emit a compact, replayable record:

```text
experiment_id
model_set_hash
prior_model_weights
state_hash
candidate_interventions
chosen_intervention
predicted_outcomes_by_model
expected_information_gain
estimated_cost
observed_outcome
posterior_model_weights
causal_graph_delta
prediction_error_before
prediction_error_after
seed
```

This turns each selected experiment into an external proof step: each reproducible result reduces the amount of trust required in the next causal update.

## Relation to the MorphoMatter trajectory

Earlier stages:

```text
observe
  ↓
model
  ↓
predict
  ↓
control
```

Experiment 053 adds:

```text
observe
  ↓
uncertainty
  ↓
choose discriminating experiment
  ↓
falsify competing explanations
  ↓
update causal model
  ↓
better prediction and control
```

The core shift is from **using a model** to **actively testing whether the model deserves to be trusted**.

## Claim boundary

A successful synthetic result would show only that, inside the declared simulator and intervention envelope, active experiment selection can identify known synthetic causal mechanisms more efficiently than selected baselines.

It would **not** demonstrate:

- discovery of a new physical law;
- autonomous laboratory science;
- correctness of a causal model for a real material;
- real-world safety of proposed interventions;
- physical energy or cost savings without external calibration.

Any physical claim requires independently measured data and reproducible laboratory evidence.

## Next experiment

**Experiment 054 — Closed-Loop Causal Discovery and Control**

Test whether the system can alternate between two modes:

1. **epistemic mode** — intervene to learn which causal model is correct;
2. **control mode** — use the improved model to reach a target with minimal intervention.

The key question becomes:

> Does spending some actions on learning first reduce total control cost and failure later?

Conceptually:

\[
learn \rightarrow update \rightarrow control \rightarrow detect\ mismatch \rightarrow learn\ again
\]
