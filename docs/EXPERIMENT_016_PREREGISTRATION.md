# Experiment 016 — Environment chemistry / screened-interaction window preregistration

## Question

Can an environment-only ionic-strength-like coordinate reshape a two-channel colloidal interaction landscape enough to create a bounded **reversible assembly window**, while geometry and interface nucleation remain fixed?

This is a synthetic, dimensionless software experiment inspired by classical DLVO logic. It does not predict physical salt concentration, Debye length, aggregation rate, or a real material phase diagram.

## Frozen base

Experiment 016 is stacked on the frozen Experiment 015 result head:

`7a2ff6f65d1773d261de1b64fceda759f4b986a1`

Frozen controls:

- geometry is not varied;
- transport geometry is not varied;
- particle/material descriptors are not varied;
- interface coordinate is fixed at the unassisted `theta = 180°` control;
- the Experiment 015 hard-endpoint interface nucleation surface must remain `IC-C1 = 0.700000` for every environment point;
- attraction parameters are fixed across the environment sweep.

Only the ionic-strength-like environment coordinate changes electrostatic screening.

## Frozen environment grid

Dimensionless ionic-strength-like values:

`I = (0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00)`

Screening coordinate:

`kappa(I) = sqrt(I)`

The corresponding screening-length-like descriptor is:

`lambda_D_like = 1 / kappa`.

This preserves only the qualitative Debye relation `lambda_D ∝ I^-1/2`; no physical unit mapping is claimed.

## Frozen two-channel pair potential

Interparticle surface separation is `h >= 0`.

Electrostatic repulsion channel:

`U_rep(h, I) = R0 / (1 + kappa(I))^2 * exp(-kappa(I) * h)`

with:

`R0 = 3.0`.

Fixed short-range attractive channel:

`U_attr(h) = -A0 * exp(-h / lambda_attr)`

with:

- `A0 = 1.0`;
- `lambda_attr = 0.18`.

Total interaction:

`U_total(h, I) = U_rep(h, I) + U_attr(h)`.

No environment coordinate may modify `A0` or `lambda_attr`.

## Frozen numerical scan

Separation grid:

- `h_min = 0.0`;
- `h_max = 3.0`;
- `dh = 0.0025`.

For each `I`, record:

- `barrier_height = max(0, max_h U_total)`;
- `well_depth = max(0, -min_h U_total)`;
- separation of the barrier maximum;
- separation of the minimum;
- `kappa` and screening-length-like descriptor.

## Frozen regime thresholds

These thresholds are algorithmic and dimensionless.

Contact-access barrier threshold:

`B_ACCESS = 0.50`

Minimum useful reversible bond depth:

`W_MIN = 0.15`

Kinetic-trap risk depth:

`W_TRAP = 0.55`

Classification:

1. `DISPERSED_BARRIER` if `barrier_height > B_ACCESS`;
2. `ACCESSIBLE_BUT_WEAK` if barrier is accessible but `well_depth < W_MIN`;
3. `REVERSIBLE_ASSEMBLY` if `W_MIN <= well_depth <= W_TRAP`;
4. `KINETIC_TRAP_RISK` if `well_depth > W_TRAP` once the barrier is accessible.

This classification is a declared synthetic architecture for distinguishing access, reversible binding, and over-binding. It does not claim that these numeric thresholds are physical constants.

## Continuous critical environment coordinates

Independently of the seven-point descriptive grid, solve two roots over:

`I ∈ [0.001, 100]`

using log-space bisection with `60` iterations:

- `I_access`: barrier height crosses downward through `B_ACCESS`;
- `I_trap`: well depth crosses upward through `W_TRAP`.

A resolved reversible environment window requires:

`I_access < I_trap`.

## Primary preregistered result rule

Protocol/numerical/control mismatch fails CI.

The positive label is:

`SCREENING_CREATES_REVERSIBLE_ASSEMBLY_WINDOW`

only if all conditions hold:

1. barrier height is monotonically non-increasing across the frozen `I` grid;
2. well depth is monotonically non-decreasing across the frozen `I` grid;
3. both continuous roots exist and `I_access < I_trap`;
4. the frozen discrete grid contains at least one `REVERSIBLE_ASSEMBLY` point;
5. at least one higher-`I` point is `KINETIC_TRAP_RISK`;
6. the fixed Experiment 015 control remains exactly `IC-C1(theta=180°, lambda=1.00) = 0.700000` at every `I`.

Otherwise the scientific label is:

`SCREENING_WINDOW_NOT_RESOLVED`.

A negative scientific result does not fail CI.

## Interpretation boundary

A positive result would support only this software-level causal decomposition:

`environment ionic-strength-like coordinate`
`-> screening length / electrostatic repulsion`
`-> total pair-potential barrier and well depth`
`-> declared interaction regime`.

The attractive channel is fixed, so any change comes from the repulsive screening channel by construction.

The experiment does **not** establish a physical salt concentration, DLVO fit, aggregation rate, crystal yield, real kinetic trapping threshold, or real phase boundary.

## Non-claims

Experiment 016 does not establish:

- a calibrated DLVO model;
- a real Debye length;
- a real ionic-strength or pH threshold;
- a real colloid material pair;
- a physical self-assembly optimum;
- physical energy savings;
- water-memory or anomalous-field effects.

The narrower supported question is whether MorphoMatter can represent **environment chemistry as an independent causal channel that changes interaction balance while interface nucleation remains fixed as a negative control**.
