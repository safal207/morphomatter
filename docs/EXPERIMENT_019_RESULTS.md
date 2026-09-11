# Experiment 019 — Orientation kinetics, reversibility, and path dependence — results

## Provenance

Preregistration before any Experiment 019 result:

`d5ad859a85775953e25662811672289ef9f8bac0`

First completed scientific implementation / CI head:

`25cb8598734d8b64a867f8327c36991a845cb923`

First completed exact-head GitHub Actions push run:

`34645945619` — **SUCCESS**.

The run passed `82` unit tests and Experiments 002–019.

## Frozen result

`ORIENTATION_KINETICS_REACHABLE_WITH_PATH_MEMORY`

All three preregistered primary criteria passed.

## A. Slow-anneal kinetic reachability

| particle | motif | successes | mean final quality |
|---|---|---:|---:|
| isotropic4 | square_torus9 | `32/32` | `1.000000000` |
| axial2 | axial_ring6 | `32/32` | `1.000000000` |
| corner2 | corner_loop4 | `32/32` | `1.000000000` |
| tri3 | tri_ladder8 | `32/32` | `1.000000000` |

Preregistered summary:

- `reachability_passes = 4/4`;
- `no_pair_below_16 = True`;
- `reachability_ok = True`.

Within this fixed-contact orientation-only surrogate, local stochastic reorientation reached the frozen Experiment 018 perfect structural optimum for every frozen seed and matched topology/motif pair.

## B. Fast-cycle finite-rate path dependence

| particle | H(0.5) | H(1) | H(2) | H(4) | H_area | positive points | signal |
|---|---:|---:|---:|---:|---:|---:|---|
| isotropic4 | `0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `0.000000000` | `0` | no |
| axial2 | `0.125000000` | `0.078125000` | `0.093750000` | `0.031250000` | `0.082031250` | `4` | yes |
| corner2 | `0.015625000` | `0.125000000` | `0.148437500` | `0.070312500` | `0.089843750` | `4` | yes |
| tri3 | `-0.015625000` | `0.036458333` | `0.096354167` | `0.096354167` | `0.053385417` | `3` | yes |

Preregistered summary:

- `path_memory_passes = 3/4`;
- `path_memory_ok = True`.

The isotropic topology showed no path-memory signal, while all three anisotropic directional topologies did under the frozen finite-rate cycle.

## C. Low-binding reversibility control

| particle | Q_initial | Q_relaxed | absolute delta | pass |
|---|---:|---:|---:|---|
| isotropic4 | `1.000000000` | `1.000000000` | `0.000000000` | yes |
| axial2 | `0.270833333` | `0.260416667` | `0.010416667` | yes |
| corner2 | `0.296875000` | `0.242187500` | `0.054687500` | yes |
| tri3 | `0.578125000` | `0.536458333` | `0.041666667` | yes |

Preregistered summary:

- `reversibility_passes = 4/4`;
- `reversibility_ok = True`.

After returning to beta `0` and relaxing for the frozen extra 30 sweeps, all four topologies returned close to their randomized low-binding quality baseline.

## Controls

Frozen controls remained intact:

- Experiment 018 preferred motifs and perfect static optima remained unchanged;
- all directional budgets remained exactly `2.0`;
- Experiment 017 background remained `q_rel=1.0, I=1.0 -> REVERSIBLE_ASSEMBLY`;
- Experiment 015 hard-interface control remained `IC-C1=0.700000000`.

## Strongest supported claim

Within this finite-state orientation-only surrogate:

`directional topology + finite-rate local reorientation -> topology-dependent kinetic path memory`

while the system remains able to relax back toward its low-binding random-orientation baseline after the binding coordinate is removed.

The strongest qualitative contrast is that isotropic4 has no forward/reverse memory signal under the same schedule, while axial2, corner2, and tri3 do.

## Interpretation boundary

This is **not** thermodynamic hysteresis or physical self-assembly evidence.

The contact graph and particle positions are frozen. Experiment 019 does not model:

- Brownian translation;
- collisions;
- steric exclusion;
- hydrodynamics;
- bond formation/breakage with spatial motion;
- physical temperature;
- calibrated patch chemistry;
- laboratory assembly yield.

The observed path dependence is finite-rate memory in a declared stochastic orientation Markov process.

## Next causal layer

A stronger Experiment 020 should unfreeze contact topology by introducing explicit translational occupancy on a small lattice or continuous-domain surrogate, while preserving the directional particle families and preregistered environment/interface controls.

That would test whether anisotropy still selects structure when particles must actually move into contact rather than only reorient on a predeclared contact graph.

## Non-claims

No physical programmable matter, real hysteresis loop, calibrated material phase diagram, physical temperature, material recipe, anomalous field, water-memory effect, or physical energy saving is established.
