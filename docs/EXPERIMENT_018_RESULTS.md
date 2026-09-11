# Experiment 018 — Particle anisotropy / directional interaction topology — results

## Provenance

Preregistration before any Experiment 018 scientific result:

`4c1e01c9e3c155e9371775b8af88872a3136bc6e`

First completed scientific implementation/CI head:

`abc89cd2991a5167db3f3770de7e61bbdfc2521b`

First completed exact-head GitHub Actions run:

`34642692506` — **SUCCESS**.

The run passed `75` unit tests and Experiments 002–018.

Experiment 018 evaluated the full frozen matrix:

`4 particle directional topologies × 4 contact motifs = 16 cells`.

Each cell exhaustively enumerated the complete `4^N` orientation-assignment space for the motif's `N` particles.

## Frozen result

`DIRECTIONAL_TOPOLOGY_SELECTS_STRUCTURE`

## Equal scalar directional budget

All particle families had exactly the same total directional-affinity budget:

`B = 2.0`.

- `isotropic4 = (0.5, 0.5, 0.5, 0.5)`;
- `axial2 = (1.0, 0.0, 1.0, 0.0)`;
- `corner2 = (1.0, 1.0, 0.0, 0.0)`;
- `tri3 = (2/3, 2/3, 2/3, 0.0)`.

Therefore the primary treatment was directional allocation/topology, not a larger scalar affinity budget.

## Frozen 16-cell matrix

| particle | motif | edge coverage | budget utilization | total bond strength | optimal assignments |
|---|---|---:|---:|---:|---:|
| isotropic4 | axial_ring6 | 1.000000000 | 0.500000000 | 3.000000000 | 4096 |
| isotropic4 | corner_loop4 | 1.000000000 | 0.500000000 | 2.000000000 | 256 |
| isotropic4 | tri_ladder8 | 1.000000000 | 0.750000000 | 6.000000000 | 65536 |
| isotropic4 | square_torus9 | **1.000000000** | **1.000000000** | 9.000000000 | 262144 |
| axial2 | axial_ring6 | **1.000000000** | **1.000000000** | 6.000000000 | 64 |
| axial2 | corner_loop4 | 0.500000000 | 0.500000000 | 2.000000000 | 32 |
| axial2 | tri_ladder8 | 0.666666667 | 1.000000000 | 8.000000000 | 256 |
| axial2 | square_torus9 | 0.500000000 | 1.000000000 | 9.000000000 | 1024 |
| corner2 | axial_ring6 | 0.500000000 | 0.500000000 | 3.000000000 | 128 |
| corner2 | corner_loop4 | **1.000000000** | **1.000000000** | 4.000000000 | 1 |
| corner2 | tri_ladder8 | 0.666666667 | 1.000000000 | 8.000000000 | 4 |
| corner2 | square_torus9 | 0.333333333 | 0.666666667 | 6.000000000 | 46656 |
| tri3 | axial_ring6 | 1.000000000 | 0.666666667 | 4.000000000 | 64 |
| tri3 | corner_loop4 | 1.000000000 | 0.666666667 | 2.666666667 | 16 |
| tri3 | tri_ladder8 | **1.000000000** | **1.000000000** | 8.000000000 | 1 |
| tri3 | square_torus9 | 0.722222222 | 0.962962963 | 8.666666667 | 288 |

## Unique preferred motifs

All four particle families had a unique preferred motif under the preregistered lexicographic score `(edge_coverage, budget_utilization)`:

| particle topology | unique preferred motif | score |
|---|---|---|
| `isotropic4` | `square_torus9` | `(1.0, 1.0)` |
| `axial2` | `axial_ring6` | `(1.0, 1.0)` |
| `corner2` | `corner_loop4` | `(1.0, 1.0)` |
| `tri3` | `tri_ladder8` | `(1.0, 1.0)` |

Thus:

- `unique_preferences = 4/4`;
- `distinct_unique_motifs = 4`.

## Matched topology/motif pairs

All four preregistered matched pairs achieved perfect compatibility:

- `axial2 -> axial_ring6`: coverage `1.0`, utilization `1.0`;
- `corner2 -> corner_loop4`: coverage `1.0`, utilization `1.0`;
- `tri3 -> tri_ladder8`: coverage `1.0`, utilization `1.0`;
- `isotropic4 -> square_torus9`: coverage `1.0`, utilization `1.0`.

Therefore:

`matched_perfect = 4/4`.

The preregistered positive criterion required at least `3/4`.

## Ranking selectivity

No two particle families had the same full motif ranking.

Pairwise ranking inversions:

- `isotropic4` vs `axial2`: `3`;
- `isotropic4` vs `corner2`: `4`;
- `isotropic4` vs `tri3`: `3`;
- `axial2` vs `corner2`: `4`;
- `axial2` vs `tri3`: `2`;
- `corner2` vs `tri3`: `1`.

Total:

`total_pairwise_ranking_inversions = 17`.

`identical_ranking_pairs = ()`.

This shows that the topology treatment did not merely perturb one favorite structure; it changed the relative ordering of multiple candidate contact networks.

## Frozen background controls

The scalar environment/interface background stayed unchanged:

- `q_rel = 1.00`;
- `I = 1.00`;
- Experiment 016/017 interaction regime = `REVERSIBLE_ASSEMBLY`;
- Experiment 015 hard-interface control = `IC-C1 = 0.700000000`.

The directional topology layer did not modify the Experiment 016/017 screened pair potential.

## Strongest supported claim

Within this frozen static contact-graph surrogate:

`equal scalar directional-affinity budget + same environment`

is **not sufficient** to determine structural compatibility.

Instead:

`directional interaction topology × contact-network geometry -> structural compatibility`.

Different directional port topologies selected different optimal contact networks even though all particle families had the same total directional budget and were evaluated under the same frozen environment/interface background.

The strongest supported software claim is therefore:

**equal scalar interaction budget does not imply equal structural preference inside this surrogate; directional topology can select which contact network is maximally compatible.**

## Important interpretation boundary

This result is partly structural to the preregistered particle-port and target-network families. It validates causal selectivity and architecture; it is not evidence for a newly discovered physical law.

The model performs static compatibility optimization over declared contact graphs. It does not simulate:

- translational Brownian dynamics;
- rotational diffusion;
- collision frequency;
- excluded-volume sterics;
- hydrodynamics;
- real patch chemistry;
- finite-temperature bond kinetics;
- nucleation probability;
- defect formation or annealing;
- spontaneous laboratory self-assembly.

Therefore `preferred motif` means **best compatible declared contact network in the frozen graph surrogate**, not a proven spontaneously assembled material phase.

## Next causal layer

A clean Experiment 019 should test **kinetic reachability and reversibility** rather than another static compatibility score.

The next model should start from randomized particle positions/orientations and allow frozen stochastic moves such as translation, rotation, binding, and unbinding under the same directional interaction law. It should preregister forward assembly, reverse disassembly/heating, hysteresis, target-order parameters, multiple seeds, and deterministic replay per seed.

That would test whether the statically preferred networks from Experiment 018 are dynamically reachable and reversible rather than merely graph-compatible.

## Non-claims

Experiment 018 does not establish:

- physical self-assembly yield;
- a real manufactured particle design;
- a thermodynamic phase diagram;
- real patch-binding energies;
- a physical temperature or kinetic rate;
- spontaneous assembly of any declared motif in a laboratory;
- anomalous fields, pyramid effects, water memory, or physical energy savings.
