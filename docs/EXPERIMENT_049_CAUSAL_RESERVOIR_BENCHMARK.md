# Experiment 049 — Causal Reservoir Benchmark

## Goal

Determine which mechanisms actually create useful computation in the Material Neural Network concept from Experiment 048.

The target is not to label a material as "intelligent". The target is to test whether its physical/synthetic dynamics provide measurable computational capacity, and which causal components are necessary for that capacity.

## Core hypothesis

Useful reservoir-style computation requires a combination of:

- nonlinear state transformation;
- fading memory / hysteresis;
- recurrent causal connectivity;
- sufficiently rich but stable dynamics.

A positive result requires that ablating one or more of these mechanisms measurably degrades task performance.

## Causal model

```text
input signal u(t)
      ↓
material state x(t)
      ↓
nonlinear local interactions
      ↓
recurrent causal propagation
      ↓
history-dependent state x(t+1)
      ↓
readout y(t)
```

The material dynamics act as the reservoir. Only a simple readout is trained.

## Benchmark tasks

Use several small deterministic tasks rather than one cherry-picked task:

1. delayed-memory recall;
2. parity / nonlinear temporal classification;
3. next-step prediction for a synthetic transition sequence;
4. perturbation recovery classification;
5. phase-transition early-warning prediction.

The benchmark should include both memory-dominant and nonlinearity-dominant tasks.

## Required ablations

### A — No memory

Reset or remove history-dependent state after each step.

Question:

Does delayed-memory and sequence prediction degrade?

### B — Linearized dynamics

Replace nonlinear transition terms with their linearized counterpart while preserving connectivity.

Question:

Do nonlinear classification tasks degrade?

### C — Destroyed recurrence

Randomly break or feed-forwardize recurrent causal paths while keeping local response magnitudes comparable.

Question:

Does temporal computation degrade?

### D — Shuffled topology

Preserve degree distribution where possible but shuffle causal edges.

Question:

Is performance tied to meaningful causal structure rather than generic connectivity?

### E — Static snapshot control

Give the readout only the instantaneous material state without temporal evolution.

Question:

Does the dynamic material provide information unavailable from a static feature map?

## Metrics

- task accuracy / normalized prediction error;
- memory capacity;
- nonlinear processing gain;
- causal-ablation performance drop;
- robustness to noise;
- robustness after damage;
- recovery of function after structural perturbation;
- intervention cost;
- number of trained readout parameters;
- transfer to unseen input regimes.

## Primary causal criterion

A strong positive signal requires all of the following:

1. full dynamics outperform a static baseline on at least one temporal task;
2. no-memory ablation reduces memory-task performance;
3. linearization reduces nonlinear-task performance;
4. recurrence/topology ablation reduces at least one temporal or transition task;
5. the simple readout remains fixed in capacity across comparisons;
6. performance survives moderate noise and partial damage better than chance.

Suggested labels:

- `MATERIAL_RESERVOIR_CAUSAL_CAPACITY_SIGNAL`
- `MATERIAL_RESERVOIR_CORRELATIONAL_ONLY`
- `MATERIAL_RESERVOIR_MIXED`
- `MATERIAL_RESERVOIR_NO_SIGNAL`

## Dynamic causal graph integration

For each time step maintain a causal graph:

\[
G_t = (V_t, E_t, W_t, \tau_t)
\]

where:

- `V_t` = active material/state variables;
- `E_t` = directed causal relations;
- `W_t` = effect strengths;
- `tau_t` = delays.

The benchmark should test whether computational performance is associated with specific causal motifs, such as:

- recurrent loops;
- delayed paths;
- branching / convergence;
- multiscale pathways;
- attractor switching.

## Fractal / multiscale extension

Measure whether computationally useful dynamics persist across coarse-graining levels:

```text
micro interactions
      ↓
mesoscale motifs
      ↓
macroscopic readout
```

Compare causal and computational metrics across scales rather than assuming fractality.

## Damage and repair test

After baseline evaluation:

1. remove or disable a preregistered fraction of nodes/edges;
2. measure task degradation;
3. allow the material dynamics to reorganize without retraining the readout where possible;
4. measure recovery.

This distinguishes ordinary reservoir redundancy from adaptive material recovery.

## Strongest supported claim if positive

Within the declared synthetic system, computation is carried by measurable material dynamics and depends causally on memory, nonlinear response, and recurrent interaction structure.

## Interpretation boundary

This experiment does **not** establish consciousness, cognition, biological neural processing, or a physical neural network material.

A positive result would demonstrate a reservoir-computing-like property of the synthetic material dynamics only.

## Non-claims

Experiment 049 does not establish:

- intelligence or awareness;
- a replacement for electronic neural hardware;
- physical energy advantages;
- real material implementation;
- quantum computation;
- biological equivalence.

## Next step

If causal capacity survives the preregistered ablations, Experiment 050 should test **Task-Free Material Computation / Emergent Representations**: whether useful internal state variables emerge before any specific readout task is defined.
