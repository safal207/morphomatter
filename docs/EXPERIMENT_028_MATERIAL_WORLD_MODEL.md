# Experiment 028 — Material World Model

## Goal

Build an internal predictive model of material evolution.

The system should not only search for conditions that work, but learn a compact model:

```
(material state, environment, interaction field, history)
                ↓
        predicted future state
```

## Core hypothesis

A learned world model can accelerate discovery by predicting transition outcomes before running expensive simulations.

## Architecture

```
Observation
    ↓
State Encoder
    ↓
World Model F_hat
    ↓
Future Prediction
    ↓
Planning / Experiment Selection
    ↓
New Evidence
    ↓
Model Update
```

## State representation

The model should include:

- particle properties;
- environment variables;
- interface state;
- interaction field Φ(x,t);
- causal graph G(t);
- fractal structure metrics;
- history / hysteresis state.

## Experiments

Compare:

1. No model — direct search.
2. Learned transition model.
3. Causal world model with active experiment selection.

## Metrics

- prediction error;
- transition discovery speed;
- number of experiments required;
- generalization to unseen materials;
- causal graph improvement;
- robustness after distribution shift.

## Research question

Can an AI system discover material transition laws by building an internal predictive universe of possible materials?

## Interpretation boundary

This is an architectural research direction for a synthetic simulator. It does not claim a calibrated physical material model.
