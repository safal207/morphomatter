# Experiment 026 — Active Discovery Loop

## Goal

Move from a passive simulator to an agent that chooses the next experiment based on expected information gain.

Core question:

> Can a discovery system reduce uncertainty about material transitions by selecting informative interventions?

## Architecture

```text
Observations
     ↓
Causal Graph G(t)
     ↓
Uncertainty Model
     ↓
Experiment Selection
     ↓
Virtual Experiment
     ↓
New Evidence
     ↓
Graph Update
```

## Discovery cycle

1. Observe material, environment and transition outcomes.
2. Maintain competing causal hypotheses.
3. Estimate which experiment best separates hypotheses.
4. Run the experiment.
5. Update the causal model.

## Experiment objects

### Material state

- particle properties;
- interaction parameters;
- interface properties;
- memory/history.

### Environment state

- screening-like variables;
- transport conditions;
- external fields.

### Outcome

- nucleation;
- frontier growth;
- stability;
- defects;
- reversible window.

## Selection objective

Choose experiments by expected information gain:

```
Value(experiment) = expected reduction of causal uncertainty
```

## Evaluation metrics

- causal graph improvement;
- number of experiments required to discover transition rules;
- prediction accuracy on unseen materials/environments;
- transfer to new interaction regimes.

## Interpretation boundary

This is an architecture proposal for a synthetic material-discovery system. It does not claim autonomous scientific discovery or physical material creation.

The purpose is to test whether causal experiment selection can accelerate discovery of transition landscapes.

## Connection to MorphoMatter

```text
Material
   ↓
Environment
   ↓
Interactions
   ↓
Transition Landscape
   ↓
Causal Model
   ↓
Active Discovery
```

