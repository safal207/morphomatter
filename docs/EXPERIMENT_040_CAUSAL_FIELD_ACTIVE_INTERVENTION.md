# Experiment 040 — Causal Field + Active Intervention

## Goal

Move from observing causal fields to testing whether an AI controller can apply bounded interventions to guide a self-organizing system toward a desired attractor.

## Core hypothesis

A transition is not only predicted by causal structure; it can be influenced by targeted changes in the causal field:

`C(x,t,phase) -> intervention -> transition trajectory`

## Architecture

```
State observation
      ↓
Causal field estimation C(x,t,φ)
      ↓
Attractor prediction
      ↓
Local intervention selection
      ↓
Material response
      ↓
Causal field update
```

## Intervention principles

The controller does not directly place particles.

It modifies transition conditions:

- interaction field;
- environment parameters;
- interface conditions;
- local gradients.

## Research questions

1. Can a small intervention redirect a transition path?
2. Can the controller avoid unstable attractors?
3. Can it reduce required intervention compared with brute force control?
4. Can causal-field knowledge transfer between materials?

## Metrics

- attractor reachability;
- intervention efficiency;
- causal prediction accuracy;
- robustness after intervention removal;
- recovery after perturbation.

## Interpretation boundary

This is a synthetic research architecture. It does not claim real material control or physical energy savings without calibrated experiments.
