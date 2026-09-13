# Experiment 042 — Attractor Evolution

## Goal

Study whether stable attractor states can themselves evolve under selection pressure.

## Core hypothesis

Instead of optimizing only material properties:

\[
Properties \rightarrow Structure
\]

we study:

\[
Properties \rightarrow Attractors \rightarrow Selection \rightarrow New regimes
\]

## Architecture

```text
Candidate systems
        ↓
Transition simulation
        ↓
Attractor discovery
        ↓
Fitness evaluation
        ↓
Variation
        ↓
Next generation
```

## Evolution targets

Select for:

- stability;
- adaptability;
- low intervention cost;
- recovery after perturbation;
- robustness across environments.

## Research questions

- Do independent populations converge to similar attractors?
- Can new stable regimes emerge?
- Are attractor landscapes evolvable?
- Does evolution discover universal transition patterns?

## Relation to MorphoMatter

This extends the system from controlling attractors to evolving attractor landscapes.

\[
observe \rightarrow design \rightarrow evolve \rightarrow discover
\]
