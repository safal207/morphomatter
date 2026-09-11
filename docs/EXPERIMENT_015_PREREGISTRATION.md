# Experiment 015 — Interface chemistry / wettability surrogate preregistration

## Question

Can a single interface-property coordinate shift the nucleation transition surface while leaving the propagation law unchanged?

This experiment is the first MorphoMatter property-level causal test after the geometry series. Geometry, transport, particle properties, action space, and environment are held fixed. Only a declared interface-affinity coordinate changes.

This is a synthetic software experiment. The contact-angle-like coordinate is inspired by classical heterogeneous nucleation theory but is not calibrated to a specific material/liquid/substrate system.

## Frozen base

Experiment 015 is stacked on the frozen Experiment 014 result head:

`a6f97a8698226c7011a000f2a1625a7e52a21068`

The local material law remains `NucleationConfig` with the same easy-to-hard lambda interpolation used in Experiments 007–014.

Frozen lambda grid:

`0.00, 0.20, 0.40, 0.60, 0.80, 1.00`

Frozen threshold slice:

`threshold_scale = 0.80`

Frozen frontier support:

`q = 0.25`

Frozen propagation drive:

`drive = 0.12`

## Interface coordinate

Use a contact-angle-like coordinate in degrees:

`theta = 30, 60, 90, 120, 150, 180`

For the nucleation mechanism only, define the classical spherical-cap heterogeneous shape factor:

`f(theta) = ((2 + cos(theta)) * (1 - cos(theta))^2) / 4`

with angle converted to radians for the cosine.

The effective nucleation barrier is:

`barrier_nucleation(theta) = barrier_bulk * f(theta)`

Boundary semantics:

- `theta = 180°` gives `f = 1` and therefore exactly reproduces the unassisted nucleation barrier;
- smaller theta represents stronger declared interface affinity / wetting assistance and lowers only the nucleation barrier;
- no other model coefficient changes with theta.

## Negative-control requirement

The interface coordinate must **not** modify:

- `frontier_base`;
- `frontier_neighbor_gain`;
- `frontier_drive_gain`;
- `commit_base`;
- `commit_neighbor_gain`;
- `commit_drive_gain`;
- external drive/coupling;
- geometry or transport.

Therefore the analytic C2 frontier root must be identical for every theta at a fixed lambda, to numerical precision.

Any theta-dependent C2 shift is a protocol failure.

## Surfaces

### IC-C1 — interface-assisted nucleation onset

For isolated DISORDERED material (`q=0`), solve the external drive where nucleation propensity first becomes positive:

`spontaneous_rate + nucleation_drive_gain * drive - barrier * threshold_scale * f(theta) = 0`

Thus:

`IC_C1(theta) = (barrier * threshold_scale * f(theta) - spontaneous_rate) / nucleation_drive_gain`

Clamp descriptive roots below zero to zero only when reporting the minimum non-negative external drive; retain the raw root internally for consistency tests.

### IC-C2 — frontier negative control

Use the unchanged Experiment 011 frontier equation at `q=0.25`, external propagation drive `0.12`, and `threshold_scale=0.80`.

IC-C2 must not depend on theta.

## Numerical validation

For every `(lambda, theta)` point:

1. compute analytic IC-C1;
2. independently scan/query the actual transition law with only the nucleation barrier adapter applied;
3. compute analytic and scanned IC-C2 through the unmodified frontier law;
4. require agreement within one frozen scan step.

Frozen scans:

- drive: `0.00 .. 1.20` step `0.01`;
- coupling: `0.00 .. 2.50` step `0.01`.

A root below the lower bound is consistent if the first scanned point is already active. A root above the upper bound is consistent if the scan returns `NONE`.

## Primary result rule

Protocol / analytic-vs-scan inconsistency fails CI.

At every lambda, the following ordering must be tested without retuning:

`IC_C1(30) <= IC_C1(60) <= IC_C1(90) <= IC_C1(120) <= IC_C1(150) <= IC_C1(180)`.

At `lambda = 1.00`, define a meaningful interface shift as:

`IC_C1(90) <= 0.75 * IC_C1(180)`

and require IC-C2 to be identical across all theta to within `1e-12` analytically.

Frozen labels:

- `INTERFACE_AFFINITY_SHIFTS_NUCLEATION_SURFACE` if monotonic ordering holds at all lambdas, the hard-endpoint 90° criterion passes, IC-C2 is invariant, and all scan consistency checks pass;
- `INTERFACE_AFFINITY_EFFECT_SMALL_OR_MIXED` otherwise, provided protocol integrity holds.

A negative scientific result does not fail CI.

## Interpretation boundary

The classical contact-angle shape factor is physically motivated: heterogeneous nucleation barriers can be reduced relative to homogeneous nucleation depending on contact angle / interfacial energies. But MorphoMatter's `barrier` remains synthetic and dimensionless, so this experiment does not predict a real nucleation temperature, concentration, contact angle, induction time, or material-specific rate.

The purpose is causal architecture:

`interface property -> nucleation barrier -> transition surface`

with propagation held as a negative control.

## Non-claims

Experiment 015 does not establish:

- a calibrated wettability model;
- a physical contact angle for any real material;
- a real nucleation rate or temperature;
- water-memory or anomalous-interface effects;
- physical energy savings.

The supported question is narrower: **can MorphoMatter represent an interface property as a first-class cause that shifts nucleation onset without contaminating unrelated transition channels?**
