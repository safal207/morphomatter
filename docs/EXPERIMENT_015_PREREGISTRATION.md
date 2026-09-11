# Experiment 015 — Interface Chemistry / Wettability preregistration

## Question

Can a change in **interface affinity / wettability** shift the transition surface for heterogeneous nucleation while the chamber geometry, transport field, bulk material law, external-control coordinates, and interior material properties remain fixed?

This is a synthetic software experiment with one physically motivated relation from classical heterogeneous nucleation theory. It is not a calibrated model of water, a specific coating, or any named material.

## Frozen base

Experiment 015 is stacked on the frozen Experiment 014 result head:

`a6f97a8698226c7011a000f2a1625a7e52a21068`

The experiment uses only the frozen `slab` chamber and its Experiment 014 equal-total-flux field:

- geometry: `slab`;
- total source flux: `Q_TOTAL = 1.0`;
- threshold scale: `0.80`;
- frontier support: `q = 0.25`;
- frontier external propagation drive: `0.12`;
- lambda grid: `(0.00, 0.20, 0.40, 0.60, 0.80, 1.00)`.

No geometry is varied in Experiment 015.

## Frozen interface shell

The chamber boundary is determined from the frozen slab mask.

Interface-treated cells are **active non-boundary cells at graph distance exactly 1 from the chamber boundary** under the 4-neighbor lattice.

All deeper cells are bulk-control cells.

The equal-flux source and sink cells themselves are excluded from both interface and bulk aggregate measurements.

The interface shell and bulk partition are determined only by chamber topology and are identical for every treatment.

## Physically motivated wettability surrogate

For a planar heterogeneous nucleation site, use the classical spherical-cap shape factor

`f(theta) = ((2 + cos(theta)) * (1 - cos(theta))^2) / 4`.

The contact-angle-like treatment levels are frozen at:

`theta = (30, 60, 90, 120, 150, 180) degrees`.

For interface-shell cells only:

`barrier_local = barrier_bulk * f(theta)`.

For bulk-control cells:

`barrier_local = barrier_bulk`.

All other `NucleationConfig` terms remain unchanged.

Interpretation of the surrogate:

- `theta = 180°` is the homogeneous-barrier control because `f(180°) = 1`;
- smaller theta represents greater substrate/nucleus affinity and a lower classical heterogeneous barrier;
- the theta values are not measurements of a real coating or liquid.

## Coupling to the frozen transport field

For each measured cell with frozen equal-flux field value `u_i`:

- `local_drive_i = external_drive * u_i`;
- `local_coupling_i = external_coupling * u_i`;
- `threshold_scale = 0.80`.

Experiment 015 changes only the local barrier of interface-shell cells through `f(theta)`.

## Aggregate transition surfaces

Three 50%-onset surfaces are preregistered.

### IC-C1 — interface nucleation

Minimum external drive for at least 50% of interface-shell cells to have positive isolated-nucleation probability.

### IC-C2 — interface frontier

Minimum external coupling for at least 50% of interface-shell cells to have positive frontier-growth probability at frozen `q = 0.25` and external drive `0.12`.

### BULK-C1 — specificity control

Minimum external drive for at least 50% of bulk-control cells to have positive isolated-nucleation probability.

Because interface chemistry is not applied to bulk cells, `BULK-C1` must be invariant across theta treatments up to numerical tolerance.

## Independent law check

Analytic aggregate roots derived from the frozen field and local barriers must be checked independently against numerical bisection that queries the actual unchanged `NucleationLattice._transition_probability` law using a per-cell config whose **only** changed physical-law parameter is `barrier`.

Frozen numerical search ranges:

- IC-C1 / BULK-C1 external drive: `[0, 100]`;
- IC-C2 external coupling: `[0, 120]`;
- bisection iterations: `50`;
- aggregate fraction: `0.50`.

A finite analytic root above the numerical upper bound plus numerical `NONE` is consistent out-of-range behavior.

## Primary hard-endpoint result rule

At `lambda = 1.00`, protocol/partition/analytic-vs-numerical inconsistency fails CI.

Define:

`C1_reduction = (IC_C1(theta=180) - IC_C1(theta=30)) / IC_C1(theta=180)`.

The preregistered positive label is:

`INTERFACE_WETTABILITY_SHIFTS_NUCLEATION`

only if all are true:

1. `C1_reduction >= 0.20`;
2. IC-C1 is monotonic nondecreasing with theta across the six frozen treatments;
3. max minus min `BULK-C1` across theta is `<= 1e-9`;
4. all measured analytic/numerical points are consistent.

Otherwise the label is:

`INTERFACE_WETTABILITY_EFFECT_SMALL_OR_NONMONOTONIC`.

IC-C2 is reported as a secondary mechanistic surface and does not alter the primary label.

## Why C2 is secondary

The current synthetic local transition law uses the same barrier term in nucleation and frontier-growth propensity. Therefore an interface barrier change may also move IC-C2. Experiment 015 measures that consequence rather than assuming a nucleation-only effect.

A later model may separate distinct nucleation, adhesion, and front-pinning free-energy terms.

## Non-claims

Experiment 015 does not establish:

- a measured contact angle for any real material;
- a calibrated interfacial free energy;
- a real heterogeneous nucleation rate;
- a physical water/crystal/coating transition point;
- that classical spherical-cap CNT is accurate at molecular or very small length scales;
- physical self-assembly or energy savings.

The supported question is narrower: **inside the frozen MorphoMatter surrogate, does a physically motivated interface-affinity coordinate move the heterogeneous transition surface while a bulk-control surface remains unchanged?**
