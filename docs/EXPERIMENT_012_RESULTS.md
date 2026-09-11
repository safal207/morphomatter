# Experiment 012 — Geometry-Shaped Transition Landscape results

## Provenance

Preregistration was committed before the first Experiment 012 result:

`811ff9f1c74e0960ccebb607676a329f8d1cc24d`

The first completed scientific implementation head was:

`585d2dcc1732390f666b0b3c192b64cb5c98ecb8`

GitHub Actions push run:

`34577409796`

The run passed `42` unit tests and Experiments 002–012. Experiment 012 evaluated `60` preregistered geometry-surface points and reported `0` inconsistent points.

## Frozen result

Preregistered label:

`GEOMETRY_SHIFTS_TRANSITION_SURFACES`

The analytic geometry-adjusted roots and independent numerical scans through the unchanged `NucleationLattice` law were consistent for all 60 points.

`inconsistent_points = 0`

## Frozen geometry metrics

| geometry | area | boundary cells | mean wall distance | mean connectivity | drive gain | coupling gain |
|---|---:|---:|---:|---:|---:|---:|
| slab | 225 | 56 | 2.022222 | 0.933333 | 1.000000 | 1.000000 |
| cylinder_like | 225 | 48 | 2.506667 | 0.924444 | 1.160294 | 1.072028 |
| pyramid_like | 220 | 58 | 1.868182 | 0.906818 | 0.949031 | 0.960245 |
| concave_hourglass | 213 | 68 | 1.361502 | 0.892019 | 0.781379 | 0.864171 |
| meandering_channel | 231 | 78 | 1.251082 | 0.904762 | 0.744843 | 0.849731 |

These gains are deterministic consequences of the preregistered geometry proxies. No geometry name receives a special coefficient.

## Hard-regime slice: lambda = 1.00

At the same frozen local material law, `threshold_scale = 0.80`, frontier support `q = 0.25`, and propagation drive `0.12`:

| geometry | external G-C1 nucleation root | class | external G-C2 frontier root | class |
|---|---:|---|---:|---|
| slab | 0.700000 | IN_ENVELOPE | 0.668800 | IN_ENVELOPE |
| cylinder_like | **0.603295** | IN_ENVELOPE | **0.606639** | IN_ENVELOPE |
| pyramid_like | 0.737595 | IN_ENVELOPE | 0.702604 | IN_ENVELOPE |
| concave_hourglass | **0.895852** | ABOVE_ENVELOPE | 0.803065 | IN_ENVELOPE |
| meandering_channel | **0.939795** | ABOVE_ENVELOPE | 0.821665 | IN_ENVELOPE |

Relative to slab at `lambda = 1.00`:

| geometry | C1 delta | C2 delta | preregistered >=0.05 shift? |
|---|---:|---:|---|
| cylinder_like | `-0.096705` | `-0.062161` | yes |
| pyramid_like | `+0.037595` | `+0.033804` | **no** |
| concave_hourglass | `+0.195852` | `+0.134265` | yes |
| meandering_channel | `+0.239795` | `+0.152865` | yes |

The preregistered shifted-geometry set is therefore:

`cylinder_like, concave_hourglass, meandering_channel`

The preregistered primary rule required at least two non-slab geometries to shift either G-C1 or G-C2 by at least `0.05`; the criterion passed.

## Reachability classification changes

At hard conditions the slab nucleation root remains inside the frozen external drive envelope `[0.02, 0.80]`.

For `concave_hourglass` and `meandering_channel`, G-C1 moves above that envelope:

- concave hourglass: `0.895852`;
- meandering channel: `0.939795`.

Thus, inside this declared synthetic adapter, chamber shape changes not only the numerical threshold but whether nucleation onset is reachable under the same bounded external drive range.

The same effect begins one step earlier at `lambda = 0.80`:

- slab G-C1 = `0.626667` (`IN_ENVELOPE`);
- concave hourglass G-C1 = `0.802000` (`ABOVE_ENVELOPE`);
- meandering channel G-C1 = `0.841340` (`ABOVE_ENVELOPE`).

## What happened to the pyramid-like chamber?

`pyramid_like` did **not** show a privileged effect.

At `lambda = 1.00` it moved the external thresholds slightly upward relative to slab:

- G-C1: `0.700000 → 0.737595`;
- G-C2: `0.668800 → 0.702604`.

Both shifts are below the preregistered `0.05` effect threshold.

This is important for interpretation: the Experiment 012 result supports a general **geometry / boundary-condition** effect inside the synthetic surrogate, not a special pyramid claim.

## Interpretation

The frozen local transition law is identical across geometries. What changes is the declared geometry-derived mapping between external forcing and the effective conditions delivered to that law.

Within this synthetic construction:

1. a compact cylinder-like cross-section has higher retention gain and requires less external forcing to cross the same local C1/C2 surfaces;
2. narrow/concave geometries attenuate the delivered condition enough to raise the external transition threshold;
3. in sufficiently hard regimes that shift can move nucleation onset outside the previously available control envelope;
4. the pyramid-like cross-section is close to slab and does not pass the preregistered strong-shift criterion.

The useful software abstraction is therefore:

`geometry → transport / confinement → effective local conditions → transition surface`

rather than:

`geometry → mysterious new force`.

## Important limitations

- The transport adapter is deliberately simple and hand-declared.
- Mean wall distance and graph connectivity are proxies, not calibrated heat/mass/electromagnetic transport.
- The shapes are 2D lattice cross-sections, not full 3D chambers.
- The material law remains synthetic and dimensionless.
- Equal active-cell area within ±6% reduces but does not eliminate every geometric confound.
- A positive geometry effect is partly structural to the declared adapter; Experiment 012 measures the **magnitude and reachability consequences** of that mapping rather than proving that real geometry must affect real matter by the same amount.
- `pyramid_like` is not a model or validation of the Golod/Moscow pyramid phenomenon.

## Non-claims

Experiment 012 does not establish a physical pyramid effect, anomalous fields, water-memory effects, physical nucleation shifts, a real phase diagram, or physical energy savings.

The supported software claim is narrower: **under a frozen geometry-coupled transport surrogate, equal-area chamber shapes can shift the external control values required to cross the same unchanged local MorphoMatter transition surfaces, and those shifts can change bounded reachability.**
