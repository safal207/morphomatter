# Experiment 013 — PDE Transport Geometry preregistration

## Question

When the scalar geometry gains from Experiment 012 are removed and a spatial transport field is solved directly on each chamber mask, does geometry still shift the **external** conditions required for a substantial fraction of the chamber to cross the same unchanged MorphoMatter nucleation/frontier law?

This is a synthetic diffusion/Laplace field experiment. It is not a calibrated thermal, fluid, acoustic, magnetic, electric, or molecular transport model.

## Frozen base

Experiment 013 is stacked on the frozen Experiment 012 head:

`c2115c489165d446259cb319d0bb67155cac253d`

The five Experiment 012 masks remain unchanged:

1. `slab`;
2. `cylinder_like`;
3. `pyramid_like`;
4. `concave_hourglass`;
5. `meandering_channel`.

No geometry name receives a special physical coefficient.

## PDE / graph-Laplace transport field

For each connected active-cell mask, solve a dimensionless steady scalar field `u` on the 4-neighbor lattice.

Boundary conditions are frozen as:

- **source boundary**: every active cell in the minimum active row has `u = 1`;
- **sink wall**: every other chamber-boundary active cell has `u = 0`;
- **interior**: discrete Laplace equation

  `u_i = mean(u_j for active 4-neighbors j)`.

The field is solved by deterministic Jacobi iteration from zero interior initialization until maximum update `< 1e-10`, with maximum `20_000` iterations. Failure to converge is a technical failure.

This boundary condition intentionally allows inlet width and chamber shape to affect the solved field. It is a declared synthetic transport problem, not a claim that a real pyramid or vessel has these boundary conditions.

## Core cells

`core_cells = active mask cells - all chamber-boundary cells`.

Source and sink boundary cells are excluded from transition-surface aggregation so the fixed Dirichlet cells do not trivially determine the result.

Every preregistered geometry must have at least 20 core cells.

## How the field enters the unchanged transition law

For a core cell `i` with solved field value `u_i`:

- `effective_drive_i = external_drive * u_i`;
- `effective_coupling_i = external_coupling * u_i`;
- `effective_threshold_scale = external_threshold_scale`.

No additional scalar geometry gain is applied.

The actual frozen `NucleationLattice._transition_probability` is called for local probability evaluation.

## Frozen material slice

Use the same Experiment 011/012 material interpolation:

- `lambda = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)`;
- `threshold_scale = 0.80`;
- frontier ordered-neighbor support `q = 0.25`;
- external frontier drive `0.12`.

## PDE-C1 — 50% nucleation onset

For each `(lambda, geometry)`, define `PDE-C1` as the smallest external drive for which at least 50% of core cells have strictly positive isolated-nucleation probability under the solved local field.

The analytic value is the median-style order statistic of per-core-cell external roots:

`local_C1_i = base_local_nucleation_root / u_i`

for `u_i > 0`.

If fewer than 50% of core cells have positive `u_i`, the analytic aggregate root is `+inf`.

## PDE-C2 — 50% frontier onset

For each `(lambda, geometry)`, define `PDE-C2` as the smallest external coupling for which at least 50% of core cells have strictly positive frontier-growth probability at `q = 0.25`.

For each core cell with `u_i > 0`, the unchanged local law receives:

- `drive = 0.12 * u_i`;
- `coupling_scale = external_coupling * u_i`;
- `threshold_scale = 0.80`.

The per-cell analytic root follows directly from the frozen transition equation; the aggregate root is the 50%-activation order statistic over core cells.

## Independent numerical check

The analytic aggregate roots must be independently recovered by evaluating the actual transition law across all core cells and using deterministic bisection on the external control variable.

Frozen numerical bounds:

- external drive search: `[0.0, 20.0]`;
- external coupling search: `[0.0, 30.0]`;
- bisection iterations: `40`;
- aggregate active-fraction target: `0.50`;
- analytic/numerical consistency tolerance: `1e-6` absolute units when the root is finite.

If the target fraction is not reached at the upper numerical bound, the numerical root is `NONE`. Analytic `+inf` and numerical `NONE` are considered consistent.

Any analytic/numerical mismatch is a technical failure and should fail CI.

## Reachability classification

For continuity with earlier experiments, roots are also classified against the frozen external control envelopes:

- drive envelope `[0.02, 0.80]`;
- coupling envelope `[0.00, 1.80]`.

This classification is descriptive and does not change the primary result rule.

## Primary result rule

At `lambda = 1.00`, compare each non-slab geometry with slab.

If every preregistered point is technically consistent:

- `PDE_GEOMETRY_SHIFTS_TRANSITION_SURFACES` if at least two non-slab geometries shift either `PDE-C1` or `PDE-C2` by at least `0.05` absolute external-control units relative to slab;
- otherwise `PDE_GEOMETRY_EFFECT_SMALL`.

A geometry-specific result is descriptive only. In particular, no pyramid-specific success criterion exists.

## Secondary outputs

Report for each geometry:

- core-cell count;
- source-cell count;
- solved field mean, median, minimum and maximum over core cells;
- convergence iterations and final residual;
- `PDE-C1` and `PDE-C2` over all six lambda values;
- hard-endpoint deltas versus slab;
- any reachability-class change versus slab.

## Non-claims

Experiment 013 does not establish:

- a physical pyramid effect;
- a real heat/diffusion/electromagnetic field in any named structure;
- water-memory effects;
- real freezing, boiling, nucleation or phase-transition temperatures;
- calibrated material transport;
- physical energy savings;
- causality outside the declared synthetic PDE surrogate.

The supported question is narrower: **when transport is generated by a solved spatial Laplace field rather than hand-declared geometry gains, can chamber shape shift aggregate external transition thresholds in the unchanged synthetic MorphoMatter law?**
