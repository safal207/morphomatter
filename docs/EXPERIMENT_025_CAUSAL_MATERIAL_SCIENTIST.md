# Experiment 025 — Causal Material Scientist

## Goal

Move from finding successful material configurations to discovering causal explanations and selecting informative experiments.

Core question:

> Can a system build and improve a causal model of material transitions instead of only optimizing outcomes?

## Concept

The loop:

```
Observation
    ↓
Causal Graph G(t)
    ↓
Hypothesis generation
    ↓
Virtual experiment selection
    ↓
Result
    ↓
Graph update
    ↓
New hypothesis
```

## State representation

The system observes:

- particle properties;
- environment properties;
- interface properties;
- interaction field;
- transition outcome;
- history.

Example causal graph:

```
particle property
        ↓
interaction landscape
        ↓
environment window
        ↓
nucleation
        ↓
frontier growth
        ↓
stable order
```

## Hypothesis generation

The system proposes competing explanations:

Example:

1. Particle property controls assembly.
2. Environment window is the dominant factor.
3. Interface dominates nucleation barrier.
4. History creates hysteresis.

## Experiment selection

Choose experiments by expected information gain:

```
uncertainty
    ↓
select intervention
    ↓
observe result
    ↓
reduce uncertainty
```

Possible interventions:

- change particle property;
- change environment coordinate;
- change interface parameter;
- change interaction field.

## Metrics

### Causal accuracy

Does the discovered graph predict interventions?

### Discovery speed

How many experiments are required to identify transition rules?

### Transfer

Can the discovered causal model work on unseen materials and environments?

## Position in MorphoMatter

The evolution of the project:

```
properties
    ↓
interactions
    ↓
transition landscape
    ↓
structure
    ↓
memory
    ↓
causal discovery
```

## Interpretation boundary

This is a research architecture proposal for a synthetic transition simulator. It is not a claim of autonomous scientific discovery or a calibrated physical material model.
