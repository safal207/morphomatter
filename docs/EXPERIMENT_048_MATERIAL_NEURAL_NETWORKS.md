# Experiment 048 — Material Neural Networks

## Goal

Test whether a material-like dynamical system can perform useful computation through its own physical state evolution, without embedding a conventional neural network inside the material model.

This is a software research architecture, not a claim that matter is literally intelligent.

## Core hypothesis

A distributed material system with nonlinear local interactions, memory, and state-dependent coupling may map inputs to outputs in a way that is computationally useful:

\[
Input(t) \rightarrow MaterialDynamics \rightarrow Readout
\]

The key question is whether the material dynamics itself provides useful representation, memory, and nonlinear transformation.

## Architecture

```text
Input field / perturbation
        ↓
Material state S(x,t)
        ↓
Local interactions
        ↓
Collective nonlinear dynamics
        ↓
Distributed memory
        ↓
Readout layer
        ↓
Prediction / classification / control signal
```

The readout may be simple and externally trained. The internal material dynamics should remain fixed in the primary reservoir-like test.

## Candidate state variables

- local phase/state;
- interaction potential;
- local order parameter;
- defect density;
- causal-field activity;
- hysteretic memory;
- fractal/topological descriptors;
- local transport field.

## Experiment families

### A. Static nonlinear mapping

Feed different input patterns into the same frozen material dynamics and test whether final or transient states linearly separate classes better than raw inputs.

### B. Temporal memory

Feed a time sequence and test whether the current state retains information about earlier inputs.

Possible metric:

\[
MemoryCapacity = \sum_k R^2(input_{t-k}, readout_t)
\]

### C. Nonlinear temporal task

Use a synthetic sequence task where solving requires both memory and nonlinear transformation.

Compare:

1. raw linear readout;
2. frozen material dynamics + linear readout;
3. shuffled/interactions-destroyed control;
4. conventional small recurrent baseline.

### D. Damage and recovery

Damage part of the interaction network and test whether computation degrades gracefully and whether material self-repair restores task performance.

## Link to previous MorphoMatter layers

```text
Particle properties
        ↓
Environment
        ↓
Interaction field Φ(x,t)
        ↓
Causal field C(x,t,φ)
        ↓
Memory / hysteresis
        ↓
Material computation
```

This explicitly connects Experiments 017, 019, 039, 040, and 047.

## Causal graph in time

The computational substrate should also be represented as a dynamic causal graph:

\[
G_t=(V_t,E_t,W_t,\tau_t)
\]

where edges have time-dependent strength and delay.

This lets us ask not only whether the system computes, but which causal pathways carry useful information.

## Fractal-gradient extension

A multiscale material may support computation at several scales:

```text
particle
   ↓
cluster
   ↓
domain
   ↓
macroscopic structure
```

Measure whether predictive information survives coarse-graining and whether similar causal motifs recur across scales.

Possible descriptors:

- fractal dimension;
- branching;
- connectivity;
- entropy;
- topological invariants;
- scale-specific mutual information.

## Primary metrics

- task accuracy / prediction error;
- memory capacity;
- nonlinear separability;
- robustness to noise;
- robustness to structural damage;
- recovery of computation after repair;
- intervention cost;
- information retained per unit of state complexity;
- causal-path stability over time.

## Essential negative controls

A positive result requires comparison against controls that remove the proposed material-computation mechanism:

- shuffled coupling graph;
- no-memory dynamics;
- linearized interactions;
- frozen uniform field;
- permuted temporal order;
- matched-size random feature map.

If these controls perform equally well, the material dynamics has not demonstrated a special computational contribution.

## Strongest allowed claim

If preregistered tasks and controls succeed, the strongest supported claim is:

> Within the declared synthetic surrogate, distributed material-like dynamics provide a useful nonlinear dynamical reservoir for information processing.

Not:

> The material is conscious, intelligent, or a biological neural network.

## Non-claims

Experiment 048 does not establish:

- cognition or consciousness;
- biological neural function;
- physical neuromorphic hardware performance;
- real energy efficiency;
- quantum computation;
- a laboratory material implementation.

## Next step

The next clean experiment should be **Experiment 049 — Causal Reservoir Benchmark**:

freeze one material dynamics model, preregister a small set of temporal tasks and matched controls, then test whether computation disappears when causal memory/interactions are ablated.
