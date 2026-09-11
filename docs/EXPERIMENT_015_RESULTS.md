# Experiment 015 — Interface chemistry / wettability surrogate results

## Provenance

Preregistration was committed before the first Experiment 015 result:

`cd45a3b1ff629c838972d5d51e5f3f279a39711a`

First completed scientific implementation head:

`fe95ccec7b846d760167b82e4d022e34c3f84c0d`

GitHub Actions PR run:

`34626467183`

The run passed `55` unit tests and Experiments 002–015.

Experiment 015 evaluated `36` preregistered `(lambda, theta)` interface points.

Integrity summary:

- `inconsistent_points = 0`;
- `monotonic_failures = 0`;
- `frontier_invariance_failures = 0`.

## Frozen result

`INTERFACE_AFFINITY_SHIFTS_NUCLEATION_SURFACE`

The contact-angle-like interface coordinate shifted the nucleation onset monotonically while the preregistered frontier negative-control surface remained unchanged.

## Frozen interface factor

The heterogeneous spherical-cap factor was:

`f(theta) = ((2 + cos(theta)) * (1 - cos(theta))^2) / 4`

| theta | f(theta) |
|---:|---:|
| 30° | 0.012860710 |
| 60° | 0.156250000 |
| 90° | 0.500000000 |
| 120° | 0.843750000 |
| 150° | 0.987139290 |
| 180° | 1.000000000 |

Only the nucleation barrier used this factor. Frontier and commit laws were not modified.

## Hard endpoint: lambda = 1.00

At `threshold_scale = 0.80`:

| theta | IC-C1 raw | IC-C1 external | scan | IC-C2 frontier |
|---:|---:|---:|---:|---:|
| 30° | -0.001965717 | 0.000000000 | 0.000 | 0.668800000 |
| 60° | 0.100000000 | 0.100000000 | 0.100 | 0.668800000 |
| 90° | **0.344444444** | **0.344444444** | 0.350 | 0.668800000 |
| 120° | 0.588888889 | 0.588888889 | 0.590 | 0.668800000 |
| 150° | 0.690854606 | 0.690854606 | 0.700 | 0.668800000 |
| 180° | **0.700000000** | **0.700000000** | 0.710 | 0.668800000 |

The preregistered hard-endpoint ratio was:

`IC-C1(90) / IC-C1(180) = 0.492063492`

The positive criterion required a ratio `<= 0.75`; it passed.

`theta = 180°` exactly reproduces the unassisted/bulk MorphoMatter nucleation barrier and therefore the Experiment 011 hard-endpoint C1 value of `0.700000`.

## Negative control

At every fixed lambda, IC-C2 was analytically identical for all six theta values.

At `lambda = 1.00`:

`IC-C2 = 0.668800000` for every theta.

Therefore the interface coordinate changed the intended nucleation channel without contaminating the propagation channel in this implementation.

## Interpretation

Inside this synthetic model, the causal chain is now explicitly represented as:

`interface affinity / wettability-like coordinate`
`-> heterogeneous nucleation barrier factor`
`-> nucleation onset surface IC-C1`

while:

`frontier propagation surface IC-C2`

remains unchanged.

This is the first MorphoMatter experiment in the current series whose primary treatment is an **interface property**, rather than geometry, controller state, or action-space design.

The result is partly structural to the preregistered classical shape-factor adapter. Its scientific value here is architectural and falsification-oriented: it verifies that one property channel can move one transition mechanism while an unrelated channel is held as an exact negative control.

## Important limitations

- MorphoMatter's barrier is synthetic and dimensionless.
- `theta` is contact-angle-like, not a measured physical contact angle for any real material pair.
- The spherical-cap factor is a simplified classical heterogeneous-nucleation construction.
- Real heterogeneous nucleation also depends on surface chemistry, roughness, curvature, site density, adsorption, defects, transport, and kinetic prefactors.
- Extremely small contact angles can invalidate simple spherical-cap assumptions.
- No real nucleation temperature, induction time, probability rate, or energy is predicted.

## Next causal layer

The next main experiment should move from interface affinity to **environment chemistry / screened interactions** while keeping geometry and interface fixed.

A clean Experiment 016 should separate at least two interaction channels rather than use one generic coupling scalar, for example:

`ionic-strength-like coordinate -> screening length -> electrostatic repulsion`

against a fixed attractive channel.

Then test whether the balance crosses an aggregation/order transition surface while interface IC-C1 remains fixed as a control.

## Non-claims

Experiment 015 does not establish a calibrated wettability model, a physical contact angle, a real nucleation rate or temperature, water-memory effects, anomalous surface fields, or physical energy savings.

The supported software claim is narrower: **MorphoMatter can represent a declared interface property as a first-class causal variable that shifts nucleation onset while leaving a separately modeled propagation mechanism unchanged.**
