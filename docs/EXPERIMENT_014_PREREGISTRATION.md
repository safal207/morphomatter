# Experiment 014 — Equal-Flux Geometry preregistration

## Question

Do the geometry-dependent transition-threshold differences seen in Experiment 013 persist when **total injected transport flux is held exactly constant across chamber shapes**?

Experiment 013 used Dirichlet inlet values (`u=1`) on every source cell. Because source-cell count varied by geometry, that mixed chamber shape with source-aperture strength. Experiment 014 replaces that inlet rule with equal total flux.

This is a synthetic software experiment. It is not a calibrated heat/fluid/electromagnetic model and does not test anomalous pyramid fields.

## Frozen base

Experiment 014 is stacked on the frozen Experiment 013 result head:

`863c59b4de18ba06dd880e756a6d9a889ee5f538`

The five frozen `21 × 21` masks remain unchanged:

1. `slab`;
2. `cylinder_like`;
3. `pyramid_like`;
4. `concave_hourglass`;
5. `meandering_channel`.

The MorphoMatter material transition law, lambda interpolation, threshold slice, frontier support, and local transition semantics remain unchanged.

## Equal-flux transport problem

For each geometry mask:

- source cells are the active cells on the minimum active row, as in Experiment 013;
- all other chamber-boundary cells are Dirichlet sinks with `u=0`;
- total injected source flux is fixed to `Q_TOTAL = 1.0` for **every** geometry;
- source injection is divided equally across source cells: `s_i = Q_TOTAL / N_source`;
- all non-source unknown cells have `s_i = 0`.

For every non-sink active cell `i`, solve the discrete graph-Poisson equation

`degree(i) * u_i - sum_{j in active neighbors(i)} u_j = s_i`.

Equivalently for iteration:

`u_i = (s_i + sum_j u_j) / degree(i)`.

All active-neighbor edges have unit conductance.

### Conservation check

The solved field must satisfy:

`Q_sink = sum over unknown-to-sink edges of (u_unknown - 0)`

and

`abs(Q_sink - Q_TOTAL) <= 1e-7`.

A field that fails conservation or residual tolerance is a technical failure.

## Frozen numerical protocol

- `Q_TOTAL = 1.0`;
- solver tolerance `1e-10`;
- maximum iterations `30000`;
- conservation tolerance `1e-7`;
- target active fraction `0.50`;
- threshold scale `0.80`;
- frontier ordered-neighbor support `q = 0.25`;
- frontier external propagation drive `0.12`;
- lambda grid `(0.00, 0.20, 0.40, 0.60, 0.80, 1.00)`.

## Coupling to the unchanged transition law

For each non-sink active cell:

- `local_drive_i = external_drive * u_i`;
- `local_coupling_i = external_coupling * u_i`;
- `threshold_scale = 0.80` unchanged.

No Experiment 012 geometry gain and no Experiment 013 Dirichlet source value is used.

## Aggregate surfaces

Two 50%-onset surfaces are measured using **non-sink active cells excluding source cells** so that injected source nodes cannot themselves satisfy the aggregate criterion:

- `EF-C1`: minimum external drive for at least 50% of evaluation cells to have positive isolated-nucleation probability;
- `EF-C2`: minimum external coupling for at least 50% of evaluation cells to have positive frontier probability at frozen `q=0.25` and external drive `0.12`.

Analytic roots derived from solved field values must be independently checked against numerical bisection querying the actual unchanged `NucleationLattice._transition_probability` law.

Frozen bisection search ranges:

- external drive `[0, 50]`;
- external coupling `[0, 60]`;
- `50` bisection iterations.

If an analytic root is finite but above the matching numerical search upper bound and numerical bisection returns `NONE`, that is consistent out-of-range behavior, not a scientific failure.

## Primary result rule

Protocol/solver/analytic-vs-numerical inconsistency fails CI.

At `lambda = 1.00`, compute the relative shift versus slab for each non-slab geometry:

`relative_shift = abs(root_geometry - root_slab) / root_slab`.

The preregistered primary label is:

- `EQUAL_FLUX_GEOMETRY_EFFECT_PERSISTS` if at least **two** non-slab geometries differ from slab by at least **10%** on either EF-C1 or EF-C2;
- otherwise `EQUAL_FLUX_GEOMETRY_EFFECT_COLLAPSES`.

Secondary descriptive output reports the exact roots, ratios, field statistics, source-cell counts, and any control-envelope classification changes. These do not alter the primary label.

## Interpretation boundary

Equal total flux removes the **total-input-strength** confound from Experiment 013, but does not make inlet geometry identical: source cells still occupy the minimum active row, so source aperture width/location can differ across masks. If a strong effect persists, a later experiment should attach an identical inlet throat/port to every chamber to isolate interior chamber geometry from inlet geometry.

## Non-claims

Experiment 014 does not establish:

- a physical pyramid effect;
- anomalous fields;
- water-memory effects;
- calibrated temperature, pressure, acoustic, magnetic, electric, or fluid transport;
- real phase-transition points;
- physical energy savings.

The supported question is narrower: **under a frozen equal-total-flux graph-Poisson transport surrogate, do different chamber masks still produce materially different aggregate transition thresholds?**
