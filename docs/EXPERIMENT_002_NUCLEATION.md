# Experiment 002 — Nucleation → Frontier → Ordered State

## Question

Can one global condition schedule create a small number of local nuclei and then let local coupling propagate order through a moving frontier, without commanding individual sites?

## Scope

This is a **dimensionless algorithmic toy experiment**. It is not a calibrated model of water, crystallization, magnetic colloids, phase-field dynamics, or any named material.

The point is narrower: test the control architecture `global conditions → rare local nucleation → neighbor-assisted frontier growth → ordered state`, while preserving exact seeded reproducibility and replayable transition evidence.

## Pinned reference configuration

- lattice: `9 × 9`;
- deterministic stochastic seed: `26`;
- initial state: all `DISORDERED`;
- stage 1, ticks `1..2`: `drive=0.45`, `coupling_scale=1.0`, `threshold_scale=0.8`;
- stage 2, ticks `3..24`: `drive=0.12`, `coupling_scale=1.5`, `threshold_scale=0.8`.

The intended mechanism is deliberately asymmetric:

1. Stage 1 raises the probability of rare spontaneous `DISORDERED → METASTABLE` nucleation.
2. Stage 2 lowers direct ordering drive while increasing local coupling.
3. Existing ordered neighbors then raise `frontier_growth` probability for adjacent disordered sites.
4. Metastable sites may `commit` to `ORDERED`.

The model is one-way in Experiment 002. Melting, reverse transitions, conservation laws, geometry-dependent free energy, and physically calibrated kinetics are outside this milestone.

## Transition evidence

Every accepted transition records:

- logical tick;
- site;
- before/after phase;
- mechanism: `nucleation`, `frontier_growth`, or `commit`;
- transition probability;
- deterministic pseudo-random draw;
- ordered-neighbor fraction;
- global conditions used for that step.

`replay()` reconstructs the final state only from the initial state plus the completed transition trace.

## Acceptance criteria

The pinned run must:

- observe all three mechanisms;
- reach at least `90%` ordered sites by tick 24;
- reproduce exactly under the same seed and schedule;
- replay to the exact final state;
- remain completely disordered when nucleation probability is explicitly forced to zero.

## Why this matters for MorphoMatter

Experiment 001 showed that a controller can search condition space rather than place sites directly. Experiment 002 adds a qualitatively different idea: **the external controller only needs to create favorable transition conditions; once nuclei exist, local interaction can carry part of the transformation.**

That is the architectural hypothesis we eventually want to test against a declared physical platform. Until calibration exists, no physical interpretation should be attached to the dimensionless rates or gains.
