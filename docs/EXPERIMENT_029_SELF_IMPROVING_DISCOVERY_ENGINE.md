# Experiment 029 — Self-Improving Discovery Engine

## Goal

Create a closed scientific discovery loop where the system does not only predict materials, but improves its own discovery process.

Core question:

> Can a material discovery agent become better at choosing experiments over time?

## Architecture

```text
Observation
    ↓
World Model
    ↓
Causal Graph Update
    ↓
Uncertainty Estimation
    ↓
Experiment Selection
    ↓
Virtual Experiment
    ↓
New Evidence
    ↓
Model Improvement
```

## Main components

### 1. Hypothesis generator

Creates candidate explanations:

- interaction hypothesis;
- environment hypothesis;
- interface hypothesis;
- structure hypothesis.

### 2. Experiment planner

Chooses the next experiment by expected information gain:

```
uncertainty reduction / experiment cost
```

### 3. Causal graph learner

Maintains a dynamic graph:

```
Property
   ↓
Interaction
   ↓
Transition
   ↓
Structure
```

Edges can change as new evidence appears.

### 4. Self-improvement loop

The agent improves:

- prediction accuracy;
- experiment selection;
- causal explanations;
- transfer to unknown materials.

## Evaluation

Metrics:

- number of experiments required to discover transition rules;
- causal prediction accuracy;
- ability to transfer to unseen materials;
- reduction of search space;
- robustness against misleading correlations.

## Scientific boundary

This is an architecture proposal for a synthetic material discovery environment.

It does not claim autonomous discovery of real materials without experimental validation.

## Relation to MorphoMatter

The evolution of the project:

```
Particles
  ↓
Properties
  ↓
Environment
  ↓
Interactions
  ↓
Transition surfaces
  ↓
Memory
  ↓
Causal discovery
  ↓
World model
  ↓
Self-improving discovery
```

Experiment 029 closes the loop between observation, explanation and exploration.
