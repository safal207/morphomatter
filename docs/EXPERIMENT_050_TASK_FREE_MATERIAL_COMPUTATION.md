# Experiment 050 — Task-Free Material Computation / Emergent Representations

## Goal

Test whether a material-like dynamical system develops reusable internal representations before any specific supervised task or readout objective is imposed.

This experiment asks whether useful structure can emerge from the system's own dynamics, rather than being inserted by a task-specific controller.

## Core hypothesis

A sufficiently rich dynamical material may organize its internal state into representations that preserve information about:

- recent input history;
- latent transition regime;
- proximity to critical transitions;
- damage state;
- attractor identity;
- environmental context.

These representations should be detectable even before assigning a downstream task.

We denote the internal state by:

\[
Z_t = h(S_t, H_t, E_t, \Phi_t)
\]

where:

- \(S_t\) is the observable material state;
- \(H_t\) is history / hysteresis;
- \(E_t\) is environment;
- \(\Phi_t\) is the interaction field.

The key question is whether \(Z_t\) contains reusable predictive structure without task-specific training.

## Architecture

```text
unlabelled condition trajectories
            ↓
material dynamics
            ↓
internal state Z(t)
            ↓
representation analysis
            ↓
small frozen readouts
            ↓
multiple downstream probes
```

The material dynamics must remain frozen during downstream evaluation. Only a lightweight probe/readout may be trained.

## Experimental protocol

### Phase A — Unsupervised dynamics

Expose the same material system to diverse condition trajectories without labels or task rewards.

Examples:

- gradual drive changes;
- abrupt perturbations;
- environment cycles;
- damage and recovery;
- approach to transition thresholds;
- alternate histories that reach similar final states.

Collect internal trajectories \(Z_t\).

### Phase B — Freeze the material

After exposure, freeze all material dynamics and parameters.

No task-specific adaptation is allowed.

### Phase C — Probe latent information

Train minimal readouts on top of frozen states for several unrelated tasks:

1. recover recent input history;
2. classify current transition regime;
3. predict near-future transition;
4. identify prior damage;
5. distinguish histories leading to the same apparent macrostate;
6. estimate attractor basin membership.

If one frozen representation supports multiple tasks, this is stronger evidence of reusable representation than success on one task alone.

## Baselines

Compare against:

1. raw instantaneous material state only;
2. shuffled-time state;
3. shuffled-node topology;
4. memory-disabled dynamics;
5. linearized dynamics;
6. random fixed features with matched dimensionality;
7. task-trained reservoir from Experiment 049.

## Falsification tests

The claim should fail if performance disappears when:

- temporal history is destroyed;
- causal recurrence is removed;
- state trajectories are phase-randomized;
- latent features are replaced with matched random projections;
- the same performance is achievable from a trivial instantaneous observable.

## Metrics

- linear-probe accuracy;
- probe sample efficiency;
- future-state prediction error;
- memory reconstruction error;
- mutual-information-like proxy between latent state and hidden variables;
- transfer across environments;
- transfer across damage regimes;
- representation stability under noise;
- representation drift over time;
- task diversity supported by one frozen state space.

## Strong criterion

A useful result requires all three:

1. one frozen material representation supports multiple downstream tasks;
2. at least one task requires temporal or causal structure not available in an instantaneous baseline;
3. ablations identify which physical/dynamical mechanisms carry the representation.

## Causal interpretation

The objective is not merely to find correlation in a high-dimensional state.

For candidate latent feature \(z_i\), test whether interventions on the underlying mechanism alter both:

\[
z_i
\]

and the downstream predictive capability.

This connects emergent representation to the causal analysis developed in Experiments 021, 039, and 049.

## Fractal / multiscale extension

Ask whether useful representations exist simultaneously at multiple spatial scales:

\[
Z^{micro}_t \rightarrow Z^{meso}_t \rightarrow Z^{macro}_t
\]

Compare whether compressed macro features preserve the same predictive information as the microscopic state.

This creates a bridge to causal renormalization from Experiment 038.

## Interpretation boundary

Positive evidence would support only a bounded claim:

> The simulated material dynamics contain reusable latent representations that can support multiple downstream predictions with lightweight readouts.

It would **not** establish consciousness, semantic understanding, autonomous goals, or general intelligence.

This remains a synthetic computational experiment until independently calibrated and reproduced in a physical material system.

## Relation to MorphoMatter

The conceptual progression becomes:

```text
self-organization
      ↓
memory
      ↓
reservoir-like computation
      ↓
emergent latent representation
      ↓
reusable prediction
```

This tests whether the same dynamical substrate that organizes matter can also become an information-bearing substrate without a task-specific controller defining every useful feature in advance.

## Next experiment

Experiment 051 — Predictive Material State / Self-Supervised World Model

Test whether the material's latent state can be optimized only for predicting its own future, then transferred to transition control, anomaly detection, and damage recovery without retraining the substrate.
