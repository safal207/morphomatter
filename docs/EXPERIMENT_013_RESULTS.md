# Experiment 013 — PDE Transport Geometry results

## Provenance

Preregistration was committed before the first Experiment 013 result:

`74060d8f46826fd148922fe039b812abdaf757db`

Pre-run numerical-bound clarification:

`4c87dd9b3b71c9e53e33948d6ae0f542658eb062`

The first completed scientific implementation head was:

`91d53966cecd7eb58ab6566cf092f6e609fe78cb`

GitHub Actions PR run:

`34580711293`

The run passed `46` unit tests and Experiments 002–013. Experiment 013 evaluated `60` preregistered PDE/transition-surface points with:

`inconsistent_points = 0`

## Frozen result

Preregistered label:

`PDE_GEOMETRY_SHIFTS_TRANSITION_SURFACES`

The solved-field analytic aggregate roots and independent actual-law bisection were consistent under the frozen numerical-bound semantics.

## Solved field statistics

| geometry | core cells | source cells | mean core field | median core field | min core | max core |
|---|---:|---:|---:|---:|---:|---:|
| slab | 169 | 15 | 0.250000 | 0.155745 | 0.005618 | 0.856110 |
| cylinder_like | 177 | 5 | 0.086804 | 0.040955 | 0.003715 | 0.703776 |
| pyramid_like | 162 | **1** | 0.002765 | **0.000095** | 0.000001 | 0.268297 |
| concave_hourglass | 145 | 15 | 0.154943 | 0.010749 | 0.000017 | 0.812139 |
| meandering_channel | 153 | 11 | 0.108383 | 0.004419 | 0.000015 | 0.778987 |

All five Jacobi solves converged below the frozen `1e-10` residual target.

## Hard-regime aggregate surfaces — lambda = 1.00

`PDE-C1` is the external drive needed for at least 50% of core cells to have positive isolated-nucleation probability.

`PDE-C2` is the external coupling needed for at least 50% of core cells to have positive frontier-growth probability at the frozen support/drive slice.

| geometry | PDE-C1 | PDE-C2 | C1 class | C2 class |
|---|---:|---:|---|---|
| slab | `4.494526` | `4.918669` | ABOVE_ENVELOPE | ABOVE_ENVELOPE |
| cylinder_like | `17.092054` | `19.027900` | ABOVE_ENVELOPE | ABOVE_ENVELOPE |
| pyramid_like | `7280.441823` | `8153.979642` | ABOVE_ENVELOPE | ABOVE_ENVELOPE |
| concave_hourglass | `65.120545` | `72.819811` | ABOVE_ENVELOPE | ABOVE_ENVELOPE |
| meandering_channel | `158.402454` | `177.295549` | ABOVE_ENVELOPE | ABOVE_ENVELOPE |

Hard-endpoint deltas versus slab:

| geometry | PDE-C1 delta | PDE-C2 delta | >=0.05 shift? |
|---|---:|---:|---|
| cylinder_like | `+12.597528` | `+14.109232` | yes |
| pyramid_like | `+7275.947298` | `+8149.060974` | yes |
| concave_hourglass | `+60.626020` | `+67.901142` | yes |
| meandering_channel | `+153.907929` | `+172.376880` | yes |

Therefore all four non-slab geometries pass the preregistered `>=0.05` shift threshold, and the primary positive label is triggered.

## Reachability result

`reachability_changes = NONE`

This is important: the solved field attenuates the externally applied condition so strongly that even the slab aggregate roots already lie above the older frozen control envelopes (`drive <= 0.80`, `coupling <= 1.80`) at the hard endpoint.

Therefore Experiment 013 does **not** show that one shape uniquely changes hard-endpoint reachability relative to slab under those old bounds. Instead it shows large relative threshold separation in a transport problem whose absolute calibration is much harsher than the earlier scalar adapter.

## Why the pyramid-like result is not evidence of a pyramid anomaly

The large pyramid-like shift has a transparent declared cause inside this PDE problem.

The source boundary is defined as **all active cells in the minimum active row**. Under the frozen masks:

- slab source width = `15` cells;
- cylinder-like = `5` cells;
- pyramid-like = **`1` cell**;
- concave hourglass = `15` cells;
- meandering channel = `11` cells.

The pyramid-like chamber therefore receives the unit Dirichlet source through a single apex cell, while almost its entire remaining boundary is fixed at zero. Its median core field collapses to about `9.5e-5`, which mechanically drives very large aggregate external thresholds.

This is a legitimate consequence of the **preregistered boundary-value problem**, but it mixes two factors:

1. chamber/domain geometry;
2. source-aperture geometry / inlet width.

Experiment 013 therefore does **not** isolate a pure chamber-shape effect.

## Relation to Experiment 012

Experiment 012 used hand-declared scalar transport proxies and found the cylinder-like shape easier than slab while pyramid-like was close to slab.

Experiment 013 replaces those scalar gains with a solved Laplace field and obtains a qualitatively different ranking. That difference is informative: conclusions about geometry are strongly dependent on the actual transport/boundary model rather than on shape names alone.

The software chain is now more explicit:

`geometry + boundary conditions -> solved field u(x,y) -> local effective conditions -> transition law`.

## Strongest next causal test

The next experiment should keep the same masks and Laplace solver but **normalize the source boundary independently of chamber shape**.

A clean design would use either:

- a fixed centered source aperture of the same cell count in every geometry; or
- equal total injected flux (Neumann-style boundary condition) across geometries.

Then compare the chamber shapes again while holding source area/flux constant.

If geometry-dependent transition shifts persist after source normalization, the case that chamber shape itself changes transport becomes substantially stronger. If the dramatic pyramid-like separation collapses, the current result is mainly an inlet-aperture effect.

A second calibration axis should also rescale the source strength so the slab hard-endpoint aggregate root lies inside a useful transition envelope; otherwise every geometry is saturated into `ABOVE_ENVELOPE` and reachability comparisons lose resolution.

## Important limitations

- The field is a dimensionless discrete Laplace surrogate, not calibrated heat/mass/electromagnetic transport.
- Dirichlet source/sink boundary conditions are synthetic.
- Source width varies with geometry by preregistration.
- The masks are 2D cross-sections, not 3D chambers.
- The local material law remains synthetic and one-way.
- Aggregate 50% onset is a declared software metric, not a thermodynamic phase boundary.
- A positive primary label is partly structural to differences in the solved boundary-value problem.

## Non-claims

Experiment 013 does not establish a physical pyramid effect, anomalous fields, water-memory effects, real nucleation changes, real freezing/boiling points, or physical energy savings.

The supported software claim is narrower: **under the frozen graph-Laplace boundary-value problem, chamber masks produce substantially different solved fields and therefore substantially different aggregate external transition thresholds in the unchanged synthetic MorphoMatter law. The present design does not separate chamber shape from source-aperture geometry.**
