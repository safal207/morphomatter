# Experiment 020 — Translational self-assembly with directional particles — preregistration

## Scientific question

When the Experiment 018 directional particle families are allowed to move as well as rotate, do their directional interaction topologies still produce distinct emergent contact structures without a predeclared contact graph?

This experiment is a synthetic lattice Monte Carlo surrogate. It is not calibrated Brownian dynamics, molecular dynamics, thermodynamics, or a laboratory material model.

## Causal boundary

Experiment 020 unfreezes **particle positions/contact topology** while preserving:

- the four Experiment 018 particle directional topologies and exact total directional budget `B = 2.0`;
- the Experiment 017/016 background `q_rel = 1.0`, `I = 1.0`, classified as `REVERSIBLE_ASSEMBLY`;
- the Experiment 015 hard-interface control `IC-C1 = 0.700000000`;
- no target-specific particle labels, pair affinities, or declared target edges.

The treatment is directional topology only:

- `isotropic4 = (0.5, 0.5, 0.5, 0.5)`;
- `axial2 = (1.0, 0.0, 1.0, 0.0)`;
- `corner2 = (1.0, 1.0, 0.0, 0.0)`;
- `tri3 = (2/3, 2/3, 2/3, 0.0)`.

All four have total directional budget exactly `2.0`.

## Frozen spatial model

- periodic square lattice: `6 × 6`;
- particle count: `8` for every topology;
- one particle maximum per lattice site (excluded-volume occupancy);
- orientations: four quarter-turn states `0,1,2,3`;
- nearest-neighbor contacts only (`N,E,S,W`);
- every undirected contact is counted once;
- contact strength is the frozen Experiment 018 `bond_strength`: minimum of the two reciprocal facing port weights;
- system binding score is the sum of all nearest-neighbor contact strengths.

There is no motif-specific field, site preference, particle identity preference, or target graph.

## Frozen stochastic move kernel

For each elementary proposal:

1. choose one of the 8 particles uniformly;
2. choose move class with equal probability:
   - translation;
   - rotation;
3. translation: choose one cardinal neighboring site uniformly; reject immediately if occupied, otherwise propose moving the particle there with orientation unchanged;
4. rotation: choose clockwise or counter-clockwise quarter-turn with equal probability, position unchanged;
5. let `delta = score_new - score_old`;
6. accept if `delta >= 0`; otherwise accept with probability `exp(beta * delta)`.

At `beta = 0`, every valid translation and every rotation proposal is accepted.

Randomness is supplied only by a deterministic `random.Random(seed)` stream.

## Frozen anneal protocol

- seeds: integers `20001..20032` inclusive (`32` seeds);
- initial state: 8 distinct lattice sites sampled without replacement plus independent random quarter-turn orientations;
- beta schedule: `(0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`;
- sweeps per beta: `300`;
- one sweep = `8` elementary proposals;
- every topology uses exactly the same seed set and schedule.

Total primary trajectories: `4 topologies × 32 seeds = 128`.

## Frozen structural metrics

For a state, define an **active bond** as a nearest-neighbor contact with positive directional bond strength.

For every particle, define active-bond degree and the lattice directions of its active neighbors.

Per-state metrics:

- `binding_utilization = total_bond_strength / N` because `N * B / 2 = N` is the system directional-budget denominator for `B=2`;
- `largest_component_fraction`: fraction of particles in the largest connected component of the active-bond graph;
- `mean_active_degree`;
- `axial_fraction`: fraction of all particles with degree exactly 2 whose two active-bond directions are opposite;
- `corner_fraction`: fraction of all particles with degree exactly 2 whose two active-bond directions are orthogonal;
- `branch_fraction`: fraction of all particles with active degree at least 3;
- `cross_fraction`: fraction of all particles with active degree 4.

Metrics are recorded after the first `beta=0` stage and after final `beta=8`.

## Frozen topology-signature checks

Using the median final (`beta=8`) metric across the 32 seeds:

1. `axial2` signature passes if
   `median(axial_fraction) >= median(corner_fraction) + 0.10`.
2. `corner2` signature passes if
   `median(corner_fraction) >= median(axial_fraction) + 0.10`.
3. `tri3` signature passes if its median `branch_fraction` is at least `0.10` greater than both the `axial2` and `corner2` median branch fractions.
4. `isotropic4` signature passes if its median `mean_active_degree` is at least `0.25` greater than both the `axial2` and `corner2` median mean active degrees.

These checks test different structural consequences rather than an exact predeclared target motif.

## Frozen assembly checks

For each topology calculate per-seed change:

`delta_utilization = final_binding_utilization - beta0_binding_utilization`.

A topology has an assembly-gain signal if median `delta_utilization >= 0.10`.

A topology has a connectivity signal if median final `largest_component_fraction >= 0.50`.

## Frozen controls

The implementation must verify:

- directional budgets remain exactly `2.0`;
- the particle topology definitions are exactly those frozen in Experiment 018;
- `q_rel=1.0, I=1.0` still maps to Experiment 016/017 `REVERSIBLE_ASSEMBLY`;
- Experiment 015 hard-interface control remains `0.700000000`;
- no two particles ever occupy the same site;
- all coordinates remain within the periodic `6×6` lattice;
- repeated same-seed runs reproduce the exact final positions, orientations, proposal count, accepted count, and recorded metrics.

## Frozen primary label

Return:

`TRANSLATIONAL_DYNAMICS_PRESERVE_DIRECTIONAL_SELECTION`

iff all are true:

1. at least `3/4` topology-signature checks pass;
2. at least `3/4` topologies have the assembly-gain signal;
3. at least `3/4` topologies have the connectivity signal;
4. all frozen controls pass;
5. deterministic replay has zero failures across the 128 primary trajectories.

Otherwise return:

`TRANSLATIONAL_SELECTION_MIXED_OR_NEGATIVE`.

A negative or mixed result is retained without retuning this preregistered protocol.

## Interpretation boundary

A positive result would support only the software claim that directional interaction topology can remain structurally selective after explicit translational occupancy dynamics are introduced in this declared lattice surrogate.

It would not establish physical programmable matter, real colloidal self-assembly yield, real Brownian motion, hydrodynamics, calibrated temperature, real bond energies, a manufactured particle recipe, or a laboratory phase transition.
