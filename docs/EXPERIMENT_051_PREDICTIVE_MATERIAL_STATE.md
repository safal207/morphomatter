# Experiment 051 — Predictive Material State / Self-Supervised World Model

## Goal

Test whether a material-like dynamical system can form internal states that are useful because they predict its own future, without task-specific labels.

## Core hypothesis

A useful internal representation should encode enough of the current state, recent history, interaction structure, and environment to predict future state transitions:

\[
Z_t = E(X_{\le t})
\]

\[
\hat Z_{t+1:t+h} = F(Z_t, U_t, E_t)
\]

where:

- \(X_{\le t}\) is the observed material history,
- \(Z_t\) is a latent predictive state,
- \(U_t\) is an intervention or control input,
- \(E_t\) is the environment,
- \(h\) is the prediction horizon.

The key question is not whether a flexible predictor can memorize trajectories, but whether the learned state contains reusable predictive structure.

## Research questions

1. Can the same latent state predict several future observables?
2. Does predictive pretraining improve downstream transition forecasting?
3. Does the latent state preserve history when two systems have similar current macrostate but different past trajectories?
4. Does it reveal approaching bifurcations or attractor changes before coarse observables do?
5. Can the model predict recovery after damage?
6. Can it transfer between nearby environments or particle/property regimes?
7. Which mechanisms are necessary: memory, recurrence, topology, interaction field, causal structure?

## Architecture

```text
material trajectory X≤t
        ↓
state encoder
        ↓
predictive latent state Zt
        ↓
world model
        ↓
future latent/state predictions
        ↓
prediction error
        ↓
self-supervised update
```

Optional intervention-aware extension:

```text
Zt + candidate intervention U
        ↓
world model
        ↓
predicted future
        ↓
attractor / risk / recovery estimate
```

## Prediction targets

Use multiple targets so that success cannot be explained by one trivial observable:

- next-step local state;
- multi-step ordered fraction;
- transition-front position;
- attractor basin label discovered post hoc;
- damage-recovery trajectory;
- causal-edge activation pattern;
- fractal / multiscale structural features;
- future transition-surface crossing.

## Self-supervised objectives

Candidate objectives:

### 1. Next-state prediction

\[
\mathcal L_{next}=d(\hat X_{t+1},X_{t+1})
\]

### 2. Multi-horizon prediction

\[
\mathcal L_{multi}=\sum_{k=1}^{h}w_k d(\hat X_{t+k},X_{t+k})
\]

### 3. Latent consistency

Require predicted latent state and encoded future observation to agree:

\[
\mathcal L_{latent}=d(\hat Z_{t+k},E(X_{\le t+k}))
\]

### 4. Counterfactual/intervention prediction

Where interventions are available:

\[
\hat X_{t+1:t+h}=F(Z_t,do(U))
\]

This should be evaluated only against interventions actually simulated or measured. Do not treat observational prediction as proof of intervention causality.

## Evaluation tasks

After predictive training, freeze the encoder/world model and use lightweight readouts for:

- phase-transition early warning;
- anomaly detection;
- recovery-success prediction;
- attractor-basin classification;
- transition-time estimation;
- selection of low-cost candidate interventions.

The central test is whether predictive pretraining helps multiple downstream tasks without retraining the material dynamics themselves.

## Baselines

Compare against:

- current macrostate only;
- raw recent-history window;
- random latent features of matched dimension;
- static autoencoder without future prediction;
- linear autoregressive baseline;
- shuffled-time control;
- shuffled-topology control.

## Ablations

Remove one mechanism at a time:

- no history / Markov snapshot only;
- no nonlinear dynamics;
- no recurrence;
- randomized interaction topology;
- no environment input;
- no intervention input;
- no causal-field features;
- no multiscale features.

A mechanism should only be called computationally important if its removal produces a reproducible loss under matched evaluation.

## Metrics

- one-step prediction error;
- multi-step rollout error;
- calibration of transition probability;
- early-warning lead time;
- downstream sample efficiency;
- transfer error across environments;
- damage-recovery prediction accuracy;
- representation stability under nuisance perturbations;
- intervention-ranking regret, if intervention prediction is evaluated.

## Strong success criterion

A strong bounded result would require all of the following:

1. predictive latent state beats matched baselines on held-out trajectories;
2. benefit persists across several downstream tasks;
3. temporal shuffling substantially degrades performance;
4. at least one causal/mechanistic ablation produces an interpretable loss;
5. performance transfers to at least one held-out environment or material parameter regime;
6. uncertainty rises out of distribution rather than remaining falsely confident.

## Failure / negative result criteria

Report a negative or mixed result if:

- static snapshots perform as well as predictive states;
- random features match learned representations;
- gains disappear outside the training regime;
- multi-step rollouts diverge rapidly;
- predictive accuracy does not improve intervention selection;
- the model cannot distinguish different histories that share the same macrostate.

## Relation to Experiments 048–050

```text
Exp048
material dynamics as computational substrate
        ↓
Exp049
identify mechanisms responsible for computation
        ↓
Exp050
task-free emergent representations
        ↓
Exp051
predictive self-supervised world model
```

Experiment 051 adds a stricter requirement to emergent representation quality:

> a representation should be useful not only because a readout can decode something from it, but because it helps predict how the material state will evolve.

## Relation to the broader MorphoMatter loop

```text
observe
  ↓
encode predictive state
  ↓
predict futures
  ↓
compare with evidence
  ↓
update world model
  ↓
choose next observation/intervention
```

This creates a bridge between material computation and active causal control.

## Scientific boundary

This experiment is a synthetic computational research plan unless and until physically calibrated and independently measured.

A positive result would support claims such as:

- the modeled dynamics support predictive state representations;
- self-supervised prediction improves forecasting or control in the simulator;
- history and interaction structure contain useful predictive information.

It would **not** establish:

- consciousness;
- biological cognition;
- autonomous understanding;
- a real material world model in laboratory matter;
- new physical laws.

Those would require separate physical evidence and stronger operational definitions.

## Next experiment

**Experiment 052 — Predictive Control / Dreamed Interventions**

Use the world model to simulate candidate interventions internally and test whether predicted low-cost actions reliably move the system toward a target attractor with fewer real/simulated trials.
