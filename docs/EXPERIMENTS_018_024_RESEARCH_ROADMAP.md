# MorphoMatter Experiments 018–024 Research Roadmap

This document records the conceptual experiment sequence developed after Experiment 017.

## Experiment 018 — Particle Anisotropy

Question:

Can particles with similar scalar interaction strength produce different structures because their interaction geometry differs?

Variables:

- spherical vs anisotropic particles;
- directional binding;
- patch-like interactions;
- orientation constraints.

Hypothesis:

Energy magnitude alone does not determine final structure. Interaction geometry creates different attractors.

---

## Experiment 019 — Memory & Hysteresis

Question:

Does the transition depend on the path taken to reach the current state?

Model extension:

`state = f(current_conditions, history)`

Measure:

- forward transition;
- reverse transition;
- hysteresis loop;
- memory retention after cycling.

Goal:

Determine whether the material has path-dependent behavior.

---

## Experiment 020 — Self-Modeling Material

Question:

Can a controller learn an internal predictive model of transition dynamics?

Architecture:

Observation → World Model → Prediction → Planning → Intervention → Update

Metrics:

- prediction error;
- transition discovery speed;
- control efficiency;
- generalization.

---

## Experiment 021 — Dynamic Causal Graph Discovery

Question:

Can the system discover changing causal relationships during transition?

Representation:

`G(t)` — causal graph evolving through time.

Nodes:

- particle properties;
- environment;
- interface;
- interaction field;
- nucleation;
- frontier growth;
- stability.

Edges include:

- strength;
- delay;
- direction.

---

## Experiment 022 — Fractal Transition Geometry

Question:

Do different transition paths leave measurable geometric signatures?

Signals:

- fractal dimension;
- branching;
- connectivity;
- entropy;
- structure complexity over time.

Core idea:

`fractal metrics + causal graph + interaction field` describe how order emerges.

---

## Experiment 023 — Causal Fractal Memory

Question:

Can the final structure reveal information about the path that created it?

Compare:

- fast transition;
- slow transition;
- recovery after damage;
- cyclic transition.

Measure whether final morphology contains a history fingerprint.

---

## Experiment 024 — Artificial Material Evolution

Question:

Can evolutionary search discover useful material-property combinations?

Genome:

- particle properties;
- interaction parameters;
- interface properties;
- memory parameters.

Selection:

`order × stability / intervention`

Tests:

- convergence from different populations;
- robustness across environments;
- discovery of unexpected combinations.

---

## Long-term direction

The overall trajectory:

`properties → interactions → transition landscape → structure → memory → causal discovery → evolution`

The purpose is not to claim a new physical material, but to build a causal simulation framework for studying how properties, environments and histories create organized states.
