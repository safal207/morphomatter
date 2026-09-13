# Experiment 017 — Particle property × environment screening matrix — preregistration

## Status

This document is frozen **before any Experiment 017 scientific result**.

Experiment 017 is a synthetic, dimensionless causal-software experiment. It is not a calibrated colloid, DLVO, electrolyte, or material model.

## Question

Holding geometry, interface, attractive interaction, screening law, regime thresholds, and controller logic fixed, does a particle/object property that changes the repulsive interaction amplitude reshape the environment window found in Experiment 016?

The intended causal chain is:

`particle surface-charge-like amplitude × environment screening`
`-> repulsive interaction`
`-> pair-potential barrier / well`
`-> accessible / reversible / trap-risk regime`

## Frozen base

Experiment 016 remains the base law:

- environment grid: `I = (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00)`;
- `kappa(I) = sqrt(I)`;
- fixed short-range attractive channel;
- `B_ACCESS = 0.50`;
- `W_MIN = 0.15`;
- `W_TRAP = 0.55`;
- the same separation grid, log-space root bounds, and bisection budget;
- interface negative control fixed at Experiment 015 `theta=180°`, hard endpoint `IC-C1 = 0.700000000`.

Experiment 017 must not change these frozen Experiment 016 constants.

## Frozen particle-property coordinate

Use a dimensionless relative surface-charge-like magnitude:

`Q_REL_GRID = (0.60, 0.80, 1.00, 1.20, 1.40)`.

Only the repulsive amplitude is changed:

`U_rep(h, I, q_rel) = q_rel^2 * U_rep_Exp016(h, I)`.

The attractive channel is exactly unchanged:

`U_attr_017(h) = U_attr_016(h)`.

`q_rel = 1.00` is the exact Experiment 016 particle baseline.

No sign claim is made: this coordinate represents the magnitude of like-charge repulsion only.

## Frozen matrix

Evaluate all:

`5 particle states × 7 environment states = 35 grid points`.

For each point report:

- `q_rel`;
- `I`;
- `kappa` and screening-length-like coordinate;
- barrier height;
- well depth;
- barrier / well locations;
- regime label.

Regime labels remain exactly those from Experiment 016:

- `DISPERSED_BARRIER`;
- `ACCESSIBLE_BUT_WEAK`;
- `REVERSIBLE_ASSEMBLY`;
- `KINETIC_TRAP_RISK`.

## Frozen continuous roots

For each `q_rel`, independently solve in the unchanged Experiment 016 root interval:

- `I_access(q_rel)`: first environment coordinate where barrier `<= B_ACCESS`;
- `I_trap(q_rel)`: first environment coordinate where well depth `>= W_TRAP`.

A valid reversible interval is declared only when:

`I_access(q_rel) < I_trap(q_rel)`.

## Frozen integrity controls

1. `q_rel = 1.00` must reproduce the frozen Experiment 016 roots within `1e-9` relative/absolute tolerance:
   - `I_access = 0.753820427`;
   - `I_trap = 2.502688872`.
2. Attraction must be exactly invariant across every particle and environment state.
3. Screening length must remain environment-only and therefore identical across particle states at fixed `I`.
4. Interface hard-endpoint control must remain exactly `IC-C1(theta=180°, lambda=1.00)=0.700000000` at every matrix point.
5. All continuous-root consistency checks must pass.

Any integrity-control failure is a protocol/evidence failure and should fail CI.

## Frozen primary scientific criteria

Positive label:

`PARTICLE_PROPERTY_RESHAPES_ENVIRONMENT_WINDOW`

requires all of the following:

1. finite `I_access` and `I_trap` for all five `q_rel` values;
2. valid reversible interval `I_access < I_trap` for at least four of five particle states;
3. `I_access(q_rel)` is monotonic non-decreasing with increasing `q_rel`;
4. `I_trap(q_rel)` is monotonic non-decreasing with increasing `q_rel`;
5. the high-charge / low-charge `I_access` ratio is at least `1.50`;
6. at least one frozen environment coordinate has different regime labels for at least two particle states;
7. all integrity controls pass.

Otherwise the frozen scientific label is:

`PARTICLE_PROPERTY_EFFECT_SMALL_OR_MIXED`.

A negative or mixed scientific result does not fail CI.

## Interpretation boundary

A positive result supports only this software-level statement:

> In the declared synthetic interaction law, changing a particle-property coordinate can move the environmental screening window even when the environment law and attractive channel are unchanged.

It does **not** establish a real zeta potential, real surface charge, real ionic strength, Debye length, aggregation rate, colloidal phase boundary, or material recipe.

## Non-claims

Experiment 017 does not establish:

- calibrated electrostatics;
- a real particle size, charge, salt concentration, or pH;
- a physical self-assembly yield;
- a real kinetic-trapping threshold;
- anomalous fields, water-memory effects, or physical energy savings.
