# Experiment 019 — Orientation kinetics, reversibility, and path dependence — preregistration

Status: **preregistered before any Experiment 019 scientific result**.

## Question

Holding the Experiment 018 particle topologies, preferred contact motifs, directional budgets, background environment, interface control, and static structural objective fixed, can a **local stochastic orientation dynamics**:

1. reach the frozen Experiment 018 optimum from randomized orientations; and
2. show finite-rate forward/reverse path dependence while still relaxing back toward the randomized low-binding baseline when the directional binding coordinate is removed?

This is an orientation-only kinetic surrogate. Particle positions and contact graphs are frozen to the declared motifs; no Brownian translation, collision, steric, hydrodynamic, or laboratory self-assembly claim is allowed.

## Frozen particle → motif pairs

Exactly the unique Experiment 018 preferences:

- `isotropic4 -> square_torus9`;
- `axial2 -> axial_ring6`;
- `corner2 -> corner_loop4`;
- `tri3 -> tri_ladder8`.

No alternative motifs are introduced in Experiment 019.

## Frozen state

A state is one quarter-turn orientation `0..3` per motif node.

The Experiment 018 contact graph remains fixed.

## Frozen kinetic score

For an orientation assignment, compute the existing Experiment 018:

- covered-edge count `C`;
- budget utilization `U in [0,1]`.

The scalar kinetic score is:

`S = C + 0.01 * U`.

Because every frozen motif has at most 18 edges, one additional covered edge dominates any possible utilization-only difference. Thus the kinetic score preserves the Experiment 018 lexicographic priority: coverage first, utilization second.

No score weight may change after result observation.

## Local proposal kernel

One proposal:

1. choose one node uniformly;
2. choose one of its three other quarter-turn orientations uniformly;
3. compute `delta = S_new - S_old`;
4. accept if `delta >= 0`;
5. otherwise accept with probability `exp(beta * delta)`.

Here `beta` is a dimensionless directional-binding / inverse-noise coordinate. It is not temperature or physical bond energy.

One sweep is exactly `node_count` proposals.

All randomness uses Python's deterministic `random.Random` with frozen integer seeds.

## A. Slow-anneal kinetic reachability

Frozen beta schedule:

`BETA_SLOW = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`.

At each beta: exactly `120` sweeps.

Frozen seeds:

`SEEDS = (17001..17032)` — 32 independent integer seeds.

Initial orientations are sampled uniformly from `0..3` using the same seed.

A run is a kinetic success if at the end of beta `8.0`:

- edge coverage is exactly `1.0`; and
- budget utilization is at least `0.95`.

Primary reachability criterion:

- at least `3/4` particle→motif pairs achieve at least `24/32` successes;
- no pair may have fewer than `16/32` successes.

## B. Fast cycle / path-dependence probe

Frozen beta schedule upward:

`BETA_FAST = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)`.

Then immediately downward:

`(4.0, 2.0, 1.0, 0.5, 0.0)`.

At each beta: exactly `2` sweeps.

For each seed, record normalized order quality:

`Q = 0.99 * edge_coverage + 0.01 * budget_utilization`.

For each shared nonzero beta `0.5,1,2,4`, define:

`H(beta) = mean(Q_reverse(beta) - Q_forward(beta))`.

Frozen hysteresis summary:

`H_area = mean(H(0.5), H(1), H(2), H(4))`.

A path-dependence signal for a topology requires:

- `H_area >= 0.05`; and
- at least three of the four shared beta points have `H(beta) > 0`.

Primary path-dependence criterion:

- at least `2/4` topologies satisfy the path-dependence signal.

This is finite-rate memory in a stochastic surrogate, not thermodynamic hysteresis.

## C. Low-binding reversibility control

After the fast reverse sweep reaches beta `0`, continue for exactly `30` extra sweeps at beta `0`.

For each topology compare across the 32 seeds:

- initial randomized mean quality `Q_initial`;
- post-cycle relaxed mean quality `Q_relaxed`.

A topology passes the low-binding reversibility control if:

`abs(Q_relaxed - Q_initial) <= 0.08`.

Primary reversibility criterion:

- at least `3/4` topologies pass.

This tests return toward the low-binding random-orientation baseline, not physical disassembly or reverse phase transition.

## Frozen controls

Experiment 019 must preserve:

- all four directional budgets exactly `2.0`;
- the Experiment 018 preferred motif identities;
- static exhaustive optima unchanged;
- Experiment 017 background `q_rel=1.0, I=1.0 -> REVERSIBLE_ASSEMBLY`;
- Experiment 015 hard-interface control `IC-C1=0.700000000`.

CI fails on protocol drift, deterministic replay failure, control drift, or invalid score/probability calculations. A negative scientific result must not fail CI.

## Frozen result labels

`ORIENTATION_KINETICS_REACHABLE_WITH_PATH_MEMORY` iff all three primary criteria pass:

1. reachability;
2. path dependence;
3. low-binding reversibility.

`ORIENTATION_KINETICS_REACHABLE_NO_PATH_MEMORY` iff reachability + reversibility pass but path dependence does not.

`ORIENTATION_KINETICS_PATH_MEMORY_WITH_LIMITED_REACHABILITY` iff path dependence passes but reachability does not.

Otherwise:

`ORIENTATION_KINETICS_MIXED_OR_NEGATIVE`.

## Non-claims

Experiment 019 does not establish spontaneous physical self-assembly, real thermodynamic hysteresis, physical temperature, Brownian diffusion, translational motion, collision kinetics, steric exclusion, hydrodynamics, calibrated patch chemistry, laboratory yield, or physical energy savings.
