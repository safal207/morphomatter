# Experiment 015 — Interface Chemistry / Wettability results

## Provenance

Preregistration before the first Experiment 015 result:

`a3e54c90d5288439177037900d3b4d732d610848`

First completed scientific implementation head:

`dd488a0275896056bbffd7a220018efef92d957e`

GitHub Actions PR run:

`34597449337`

The run passed `54` unit tests and Experiments 002–015.

Experiment 015 evaluated `108` preregistered surface points with:

`inconsistent_points = 0`.

## Frozen result

Preregistered label:

`INTERFACE_WETTABILITY_SHIFTS_NUCLEATION`

At the hard endpoint (`lambda = 1.00`), the frozen results were:

| contact-angle surrogate | classical factor f(theta) | IC-C1 | IC-C2 | BULK-C1 |
|---:|---:|---:|---:|---:|
| 30° | `0.012860710` | `0.000000` | `0.000000` | `12.620275` |
| 60° | `0.156250000` | `5.994461` | `0.000000` | `12.620275` |
| 90° | `0.500000000` | `20.647589` | `16.189735` | `12.620275` |
| 120° | `0.843750000` | `35.300717` | `37.290239` | `12.620275` |
| 150° | `0.987139290` | `41.413013` | `46.091945` | `12.620275` |
| 180° | `1.000000000` | `41.961230` | `46.881377` | `12.620275` |

Primary preregistered checks:

- IC-C1 reduction, 30° versus 180°: `1.000000000` (100%);
- IC-C1 monotonic nondecreasing with theta: `True`;
- BULK-C1 span across theta: `0.000000000000`;
- inconsistent analytic/numerical points: `0`.

All primary criteria passed.

## What changed causally

Geometry was fixed to `slab`.

The equal-total-flux transport field was fixed.

The bulk material law was fixed.

Only wall-adjacent interface-shell cells received the classical planar heterogeneous-nucleation barrier factor

`f(theta) = ((2 + cos(theta)) * (1 - cos(theta))^2) / 4`.

Deeper bulk-control cells kept the original barrier.

The resulting causal pattern was therefore:

`interface-affinity coordinate -> local barrier -> interface transition surface`

while the preregistered bulk-control surface stayed invariant.

## IC-C2 interpretation

IC-C2 also moved strongly with theta.

This is expected inside the current synthetic transition law because the same `barrier` term appears in both isolated nucleation and frontier-growth propensity.

Experiment 015 therefore does **not** prove that real wettability controls front propagation in exactly the same way as nucleation.

Instead it identifies a limitation of the present surrogate: future models should separate at least

- heterogeneous nucleation free-energy barrier;
- interface adhesion / detachment;
- front-pinning or growth barrier;
- bulk phase barrier.

That decomposition is important for a physical MorphoMatter model.

## Strongest supported software claim

Inside the frozen MorphoMatter surrogate, a physically motivated interface-affinity coordinate can move the wall-adjacent heterogeneous transition surfaces by a large amount while a deeper bulk-control nucleation surface remains exactly unchanged.

This supports treating interface properties as first-class state variables rather than folding them into one generic coupling coefficient.

## Important limitations

- The contact angles are treatment coordinates, not measurements.
- The spherical-cap classical factor assumes an ideal planar heterogeneous-nucleation picture.
- At small contact angles and molecular scales, classical nucleation theory can break down.
- The barrier parameter is dimensionless and not calibrated to a real interfacial free energy.
- The equal-flux transport field is still a synthetic graph surrogate.
- The current frontier law reuses the same barrier term and is therefore not yet a mechanistically separated interface-growth model.

## Next causal layer

The next main experiment should move from interface chemistry to **environment chemistry / interaction screening** while keeping geometry and interface treatment fixed.

A clean Experiment 016 can expose separate interaction channels such as

`ionic-strength-like screening -> electrostatic repulsion range -> net pair interaction -> aggregation/order transition`.

The critical requirement is to avoid one generic `chemical_gain`: the environment variable should modify an explicit interaction term while unrelated interaction channels remain fixed.

## Non-claims

Experiment 015 does not establish a real contact angle, real coating performance, physical nucleation rate, water behavior, real phase-transition point, or physical programmable matter.
