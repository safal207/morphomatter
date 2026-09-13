# Experiment 017 — Particle property × environment screening matrix — results

## Provenance

Preregistration before any Experiment 017 scientific result:

`8ce77137afed0b1e3f5a6f83b89951d414a3c5b3`

First completed scientific implementation head:

`c33706bc2d74c58149c343b2e502a7868be5b544`

First completed exact-head GitHub Actions run:

`34638350825` — **SUCCESS**.

The run passed `69` unit tests and Experiments 002–017.

Experiment 017 evaluated:

- `35` frozen particle × environment matrix points;
- `5` particle-specific `I_access` roots;
- `5` particle-specific `I_trap` roots.

All protocol/evidence controls passed:

- `interface_control_failures = 0`;
- `attraction_invariance_failures = 0`;
- `screening_invariance_failures = 0`;
- `root_consistency_failures = 0`.

## Frozen result

`PARTICLE_PROPERTY_RESHAPES_ENVIRONMENT_WINDOW`

## Particle-specific continuous windows

| q_rel | I_access | I_trap | reversible interval valid |
|---:|---:|---:|---|
| 0.60 | `0.089401030` | `0.301613323` | yes |
| 0.80 | `0.352054698` | `1.135484431` | yes |
| 1.00 | `0.753820427` | `2.502688872` | yes |
| 1.20 | `1.273608694` | `4.403226646` | yes |
| 1.40 | `1.899081346` | `6.837097754` | yes |

All five frozen particle states retained a non-empty interval:

`I_access(q_rel) < I_trap(q_rel)`.

The roots were monotonic with increasing particle charge-like magnitude:

- `access_monotonic = True`;
- `trap_monotonic = True`.

The preregistered high/low access-root ratio was:

`I_access(1.40) / I_access(0.60) = 21.242275870`.

The positive criterion required `>= 1.50`; it passed.

## Exact Experiment 016 baseline reproduction

At `q_rel = 1.00`:

- expected `I_access = 0.753820427`;
- observed `I_access = 0.753820427`;
- expected `I_trap = 2.502688872`;
- observed `I_trap = 2.502688872`.

Thus Experiment 017 reproduces Experiment 016 exactly at the declared baseline particle property.

## Same environment, different particle regimes

Frozen environment coordinates with at least two particle-dependent regime labels:

`(0.10, 0.30, 1.00, 3.00)`.

A particularly informative slice is `I = 1.00`:

| q_rel | regime |
|---:|---|
| 0.60 | `KINETIC_TRAP_RISK` |
| 0.80 | `REVERSIBLE_ASSEMBLY` |
| 1.00 | `REVERSIBLE_ASSEMBLY` |
| 1.20 | `DISPERSED_BARRIER` |
| 1.40 | `DISPERSED_BARRIER` |

The same environment point therefore does not have a universal assembly meaning in this synthetic law.

At `I = 3.00` the ordering reverses in a useful way:

- `q_rel = 0.60, 0.80, 1.00` are `KINETIC_TRAP_RISK`;
- `q_rel = 1.20, 1.40` are `REVERSIBLE_ASSEMBLY`.

This is the core matrix-level signal.

## Negative controls

### Attractive channel

The attractive potential remained exactly the frozen Experiment 016 channel for every particle and environment state.

### Screening law

At fixed `I`, `kappa` and screening-length-like coordinates were identical for all particle states. The particle coordinate did not alter the environment law.

### Interface channel

The Experiment 015 hard-interface control remained exactly:

`IC-C1(theta=180°, lambda=1.00) = 0.700000000`

for all 35 matrix points.

## Strongest supported claim

Within the declared synthetic interaction law:

`particle property × environment property -> effective interaction landscape -> assembly regime`

is genuinely two-dimensional.

The same environment condition can be dispersing, reversibly assembling, or trap-prone depending on the particle-property coordinate, while the attractive, screening, and interface channels are held fixed as declared controls.

This is stronger than a single generic `coupling_scale`: it demonstrates a software architecture in which **material/object properties and environment properties jointly determine the transition window**.

## Important interpretation boundary

The magnitude of the shift is partly structural to the preregistered law `U_rep ∝ q_rel²`. The result validates causal architecture and interaction selectivity inside this surrogate; it does not calibrate real electrostatic amplitudes.

`q_rel` is not a physical zeta potential, surface charge density, particle radius, or ligand density.

Likewise `I` is not a physical molar ionic strength and the roots are not laboratory salt concentrations.

## Next causal layer

A clean next experiment should stop treating the particle as one scalar property and add **particle anisotropy / directional interaction** while keeping the environment-screening matrix frozen.

That would test whether two particles with similar scalar attraction/repulsion magnitudes can still have different reachable ordered structures because their interaction geometry differs.

A later reversible phase-field experiment should then test forward/reverse transition and hysteresis explicitly rather than classifying trap risk only from a static pair potential.

## Non-claims

Experiment 017 does not establish:

- real surface charge or zeta potential;
- real Debye length or ionic strength;
- a physical aggregation/crystallization rate;
- a calibrated material recipe;
- a real phase diagram;
- anomalous fields, water-memory effects, or physical energy savings.
