# Experiment 016 — Environment chemistry / screened-interaction window results

## Provenance

Preregistration was committed before the first Experiment 016 result:

`9f42c9055c3c8e7cfe0d57fee0b6e3e927d76ccf`

First completed scientific implementation head:

`80c937bf66a2b1e03bb27bc3f788720d90950058`

GitHub Actions PR run:

`34629614525`

The run passed `62` unit tests and Experiments 002–016.

## Frozen result

`SCREENING_CREATES_REVERSIBLE_ASSEMBLY_WINDOW`

The ionic-strength-like environment coordinate changed only the screened repulsive channel, while the short-range attractive channel and the Experiment 015 interface nucleation control remained fixed.

## Frozen interaction map

| I-like | kappa | screening-length-like | barrier | well depth | regime |
|---:|---:|---:|---:|---:|---|
| 0.01 | 0.100000 | 10.000000 | 2.299825 | 0.000000 | `DISPERSED_BARRIER` |
| 0.03 | 0.173205 | 5.773503 | 1.936591 | 0.000000 | `DISPERSED_BARRIER` |
| 0.10 | 0.316228 | 3.162278 | 1.419948 | 0.000000 | `DISPERSED_BARRIER` |
| 0.30 | 0.547723 | 1.825742 | 0.898047 | 0.000000 | `DISPERSED_BARRIER` |
| 1.00 | 1.000000 | 1.000000 | **0.396253** | **0.250000** | `REVERSIBLE_ASSEMBLY` |
| 3.00 | 1.732051 | 0.577350 | 0.107959 | 0.598076 | `KINETIC_TRAP_RISK` |
| 10.00 | 3.162278 | 0.316228 | 0.003492 | 0.826835 | `KINETIC_TRAP_RISK` |

Across the frozen grid:

- barrier height was monotonically non-increasing;
- well depth was monotonically non-decreasing.

## Continuous environment roots

Log-space bisection over `I in [0.001, 100]` resolved:

- `I_access = 0.753820427` — barrier crosses below `B_ACCESS = 0.50`;
- `I_trap = 2.502688872` — well depth crosses above `W_TRAP = 0.55`.

Both root checks were internally consistent and:

`I_access < I_trap`.

Therefore the declared reversible environment window is bounded between the onset of contact accessibility and the onset of over-binding/trap risk.

## Negative control

The Experiment 015 unassisted interface nucleation control was fixed at:

`IC-C1(theta=180°, lambda=1.00) = 0.700000000`

for every frozen environment point.

`interface_control_failures = 0`.

This verifies that Experiment 016 changes the environment interaction channel without modifying the interface-nucleation channel.

## Interpretation

Inside this synthetic model, the causal chain is:

`ionic-strength-like environment coordinate`
`-> shorter screening-length-like scale`
`-> weaker electrostatic-repulsion-like channel`
`-> lower access barrier`
`-> reversible assembly window`
`-> deeper attraction-dominated well at higher screening`
`-> kinetic-trap-risk regime`.

The important architectural result is that **more screening is not treated as monotonically better**. A bounded middle region emerges in which particles can approach and bind without the declared pair well becoming too deep for reversible rearrangement.

This matches the qualitative design goal for MorphoMatter: search not for maximal coupling, but for a trajectory through a multi-channel interaction landscape.

## Important limitations

- All energies and environment coordinates are dimensionless.
- The repulsive amplitude law is a declared screening surrogate, not a calibrated DLVO fit.
- The attractive channel is a fixed short-range exponential surrogate, not a material-specific van der Waals potential.
- `B_ACCESS`, `W_MIN`, and `W_TRAP` are algorithmic thresholds, not physical constants.
- `KINETIC_TRAP_RISK` is a declared risk regime, not a simulated many-body glass transition or experimentally observed aggregate.
- No Brownian dynamics, hydrodynamics, many-body packing, particle anisotropy, concentration dependence, or charge regulation is included.

## Next causal layer

The next main experiment should move to **particle/object properties** while freezing the environment window and interface control.

A clean Experiment 017 can vary one or more particle descriptors — size/shape anisotropy/surface charge proxy — and ask whether the same environment coordinate produces different interaction windows or preferred assembly regimes.

The stronger future target is then a factorial held-out test:

`particle properties × environment chemistry × interface property -> transition regime`.

## Non-claims

Experiment 016 does not establish a calibrated Debye length, real ionic strength, real pH/salt threshold, physical aggregation rate, crystal yield, real kinetic trapping boundary, anomalous field, water-memory effect, or physical energy saving.

The supported software claim is narrower: **MorphoMatter can represent environment chemistry as an independent screened-interaction channel that produces a bounded reversible-assembly window while a separately modeled interface-nucleation control remains fixed.**
