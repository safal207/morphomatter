# Experiment 018 — Particle anisotropy / directional interaction topology

## Status

Preregistered before any Experiment 018 scientific result.

## Question

Holding the scalar directional-affinity budget, environment, interface control, and particle/environment screening state fixed, can different **directional interaction topologies** prefer different ordered contact networks?

This experiment moves from the scalar particle property used in Experiment 017 to the geometry of the interaction ports themselves.

## Frozen background state

Experiment 018 is evaluated on the frozen Experiment 017 baseline environment:

- particle screening coordinate: `q_rel = 1.00`;
- environment coordinate: `I = 1.00`;
- the Experiment 017/016 interaction regime at that point must remain `REVERSIBLE_ASSEMBLY`;
- the Experiment 015 hard-interface control must remain `IC-C1 = 0.700000000`.

The directional-topology layer does **not** modify the Experiment 016/017 screened pair potential. It is an additional normalized contact-allocation surrogate used to ask which contact graph is compatible with a particle's directional ports once contact is accessible.

## Frozen scalar directional budget

Every particle family has exactly the same total directional-affinity budget:

`B = sum(port_weights[N,E,S,W]) = 2.0`.

Canonical port vectors before rotation:

- `isotropic4 = (0.5, 0.5, 0.5, 0.5)`;
- `axial2 = (1.0, 0.0, 1.0, 0.0)`;
- `corner2 = (1.0, 1.0, 0.0, 0.0)`;
- `tri3 = (2/3, 2/3, 2/3, 0.0)`.

Allowed orientations are the four cardinal rotations `0, 90, 180, 270 degrees`. Symmetry-equivalent rotations may be retained; they do not change the optimum score.

No particle family receives more total directional budget than another.

## Frozen target contact networks

The motifs are declared as finite directed-port contact graphs. Every undirected edge has a reciprocal cardinal direction at its two endpoints.

1. `axial_ring6`
   - six nodes on a periodic one-dimensional ring;
   - every node has exactly two opposite contacts, `E/W`;
   - degree = 2 for all nodes.

2. `corner_loop4`
   - four nodes in a 2x2 square loop;
   - every node has two adjacent contacts;
   - degree = 2 for all nodes.

3. `tri_ladder8`
   - two rows of four nodes with horizontal periodic cycles plus four vertical rungs;
   - every node has degree 3;
   - top row contact set is `E/W/S`, bottom row is `E/W/N`.

4. `square_torus9`
   - 3x3 periodic square lattice;
   - every node has four contacts `N/E/S/W`;
   - degree = 4 for all nodes.

The periodic motifs are used to suppress trivial free-boundary under-coordination.

## Frozen bond law

For an edge `(u,v)` with direction `d` at `u` and reciprocal direction `opp(d)` at `v`:

`bond_strength = min(port_weight_u[d], port_weight_v[opp(d)])`.

A bond is counted as covered iff `bond_strength > 0`.

For a motif with `N` particles and common directional budget `B=2`:

`budget_utilization = 2 * sum(bond_strengths) / (N * B)`.

This quantity is bounded by 1 when each directional port can serve at most one declared neighbor.

`edge_coverage = covered_edges / total_edges`.

The preregistered structural score is lexicographic, not a tuned weighted sum:

1. maximize `edge_coverage`;
2. among equal-coverage assignments, maximize `budget_utilization`;
3. deterministic tie-break by lexicographically smallest orientation tuple.

For each particle family × motif pair, the optimizer must enumerate the complete orientation assignment space. No stochastic or learned search is allowed.

## Frozen matrix

`4 particle topologies × 4 motifs = 16 particle/motif cells`.

For each cell report:

- maximum edge coverage;
- maximum budget utilization among maximum-coverage assignments;
- optimal total bond strength;
- number of globally optimal orientation assignments;
- deterministic canonical optimal orientation tuple.

For each particle family, its preferred motif is the motif with the lexicographically largest pair:

`(edge_coverage, budget_utilization)`.

A preferred motif is `UNIQUE` only if no other motif has the same pair within `1e-12` on both components.

## Frozen integrity controls

CI must fail if any of the following occurs:

- a particle family does not sum to directional budget `2.0` within `1e-12`;
- a motif contains a non-reciprocal direction pair;
- a declared node degree differs from the motif specification;
- the exhaustive optimizer omits an orientation assignment;
- any reported utilization is outside `[0,1]` by more than `1e-12`;
- `q_rel=1.0, I=1.0` no longer reproduces the Experiment 017/016 `REVERSIBLE_ASSEMBLY` background regime;
- the Experiment 015 hard-interface control differs from `0.700000000`.

Scientific negative or mixed outcomes must **not** fail CI.

## Frozen positive criterion

Label:

`DIRECTIONAL_TOPOLOGY_SELECTS_STRUCTURE`

iff all are true:

1. all 16 exhaustive matrix cells pass protocol/integrity checks;
2. all four particle families have the exact same scalar directional budget `B=2.0`;
3. at least `3/4` particle families have a `UNIQUE` preferred motif;
4. at least three distinct motifs appear among those unique preferences;
5. at least three of the declared matched topology/motif pairs reach `edge_coverage = 1.0` and `budget_utilization = 1.0`:
   - `axial2 -> axial_ring6`;
   - `corner2 -> corner_loop4`;
   - `tri3 -> tri_ladder8`;
   - `isotropic4 -> square_torus9`;
6. at the fixed background `q_rel=1.0, I=1.0`, screened interaction remains `REVERSIBLE_ASSEMBLY`;
7. interface control remains exactly `0.700000000`.

Otherwise label:

`DIRECTIONAL_TOPOLOGY_STRUCTURE_SELECTIVITY_MIXED`

## Secondary preregistered observations

Report, without affecting the primary label:

- whether all four matched topology/motif pairs achieve perfect coverage and perfect budget utilization;
- optimal-orientation degeneracy for every matrix cell;
- whether any two particle families have identical full motif ranking;
- pairwise ranking inversions between particle families.

## Interpretation boundary

This is a synthetic, dimensionless directional-contact graph surrogate.

The experiment tests a causal architecture:

`particle interaction topology × contact-network geometry -> structural compatibility`.

It does not simulate Brownian translation/rotation, hydrodynamics, steric exclusion, real patch chemistry, finite-temperature kinetics, nucleation rates, defect annealing, or a calibrated free-energy landscape.

`isotropic4`, `axial2`, `corner2`, and `tri3` are abstract port topologies, not specific manufactured particles.

## Non-claims

Experiment 018 cannot establish:

- a physical self-assembly yield;
- a real material recipe;
- a thermodynamic phase diagram;
- that a target network will spontaneously assemble in a laboratory;
- anomalous fields, pyramid effects, water memory, or physical energy savings.

A later experiment should introduce reversible orientation/translation dynamics and hysteresis so that structural preference is tested through an actual trajectory rather than static contact-graph optimization.
