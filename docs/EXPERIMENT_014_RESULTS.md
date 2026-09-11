# Experiment 014 — Equal-Flux Geometry results

## Provenance

Preregistration was committed before the first Experiment 014 result:

`0e9cc6c0a7df2e3458071a604ba69d69535e1d96`

First completed scientific implementation head:

`f8f4cd04cbbe0c32c9a3dc6366495974f06b7b5c`

GitHub Actions PR run:

`34595689621`

The run passed `50` unit tests and Experiments 002–014. Experiment 014 evaluated `60` preregistered equal-flux surface points and reported `0` inconsistent points.

## Frozen result

Preregistered label:

`EQUAL_FLUX_GEOMETRY_EFFECT_PERSISTS`

The graph-Poisson solver conserved the same total injected flux for every geometry:

`Q_TOTAL = 1.0`.

All solved sink fluxes were within the preregistered conservation tolerance.

## Equal-flux field statistics

| geometry | source cells | injection/source | sink flux | eval median | eval mean |
|---|---:|---:|---:|---:|---:|
| slab | 15 | 0.066666667 | 0.999999985 | 0.044779559 | 0.070614972 |
| cylinder_like | 5 | 0.200000000 | 0.999999983 | 0.021119951 | 0.044758705 |
| pyramid_like | 1 | 1.000000000 | 0.999999987 | 0.000130020 | 0.003778850 |
| concave_hourglass | 15 | 0.066666667 | 0.999999994 | 0.002656611 | 0.037123567 |
| meandering_channel | 11 | 0.090909091 | 0.999999995 | 0.001202127 | 0.029131709 |

Thus Experiment 014 removes unequal **total source strength**, but not inlet-aperture geometry or interior topology.

## Hard endpoint: lambda = 1.00

Aggregate 50%-onset roots:

| geometry | EF-C1 nucleation | EF-C2 frontier | C1 ratio vs slab | C2 ratio vs slab |
|---|---:|---:|---:|---:|
| slab | `15.632133` | `17.392789` | `1.000000` | `1.000000` |
| cylinder_like | `33.144016` | `37.006098` | `2.120249` | `2.127669` |
| pyramid_like | `5327.095311` | `5966.231548` | `340.778538` | `343.029039` |
| concave_hourglass | `263.493570` | `294.997598` | `16.855894` | `16.960914` |
| meandering_channel | `582.301084` | `652.062014` | `37.250265` | `37.490366` |

Every non-slab geometry exceeds the preregistered 10% relative-shift threshold on both surfaces.

Preregistered shifted set:

`cylinder_like, pyramid_like, concave_hourglass, meandering_channel`

## Interpretation

The result rules out one simple explanation for Experiment 013: the geometry separation is **not solely caused by different total injected source strength**. After total input is normalized, the solved spatial fields still differ strongly.

However, Experiment 014 does **not** isolate interior chamber shape perfectly.

The source aperture still differs across masks because source cells remain the minimum active row:

- slab: 15 source cells;
- cylinder-like: 5;
- pyramid-like: 1;
- concave hourglass: 15;
- meandering channel: 11.

Equal total flux means narrower inlets receive more injection per inlet cell. The field that results depends jointly on:

`inlet geometry + chamber topology + sink geometry`.

Therefore the extreme pyramid-like value remains interpretable as a transport/boundary-condition effect, not as evidence of an anomalous pyramid field.

## Broader project direction

Experiment 014 closes the immediate equal-total-input control, but MorphoMatter should not over-focus on chamber geometry.

The broader research object is defined in `docs/MATERIAL_ENVIRONMENT_TRANSITION_MAP.md`:

`material properties × environment properties × interface properties × interaction law × trajectory/history -> transition probability -> structure`.

The next primary experiments should begin isolating these causal layers, especially:

1. interface chemistry / wetting and heterogeneous nucleation affinity;
2. environment chemistry such as concentration, ionic-strength-like screening, and pH-like surface-charge control;
3. particle properties such as size, anisotropy, stiffness and interaction directionality;
4. reversible transition / hysteresis and history dependence;
5. reaction–diffusion coupling where the environment changes dynamically.

A fixed identical inlet throat can remain as a geometry-control follow-up, but it is not the central scientific direction.

## Important limitations

- graph-Poisson transport is synthetic and dimensionless;
- unit edge conductance is not calibrated to any material;
- all old physical control envelopes are far below the equal-flux aggregate roots, so `reachability_changes=NONE` is not informative about a real system;
- source aperture, chamber topology and sink topology remain coupled;
- the material transition law remains one-way and synthetic.

## Non-claims

Experiment 014 does not establish a physical pyramid effect, anomalous field, water-memory effect, calibrated transport, real phase diagram, real nucleation threshold, or physical energy saving.

The supported software claim is narrower: **with equal total injected graph flux, the frozen chamber masks still produce reproducibly different spatial fields and aggregate transition thresholds, so the Experiment 013 separation was not solely an unequal-total-input artifact.**
