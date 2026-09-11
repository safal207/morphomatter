# Experiment 007 — preregistered controllability boundary search

Status: **PREREGISTERED BEFORE FIRST BOUNDARY-MATRIX EXECUTION**

## Question

Between the saturated recovery regime of Experiment 005 and the impossible-for-all regime of Experiment 006, does a learned global-condition policy shift the software **controllability boundary** relative to a fixed cooperative heuristic and random schedules?

This is a simulation-only boundary experiment. It is not evidence of physical programmable matter, physical phase-transition control, physical self-repair, physical energy savings, or general AI superiority.

## Frozen difficulty axis

Define one scalar difficulty coordinate `lambda` and evaluate exactly:

`0.00, 0.20, 0.40, 0.60, 0.80, 1.00`

Only the transition-law configuration changes with `lambda`. Damage geometries, train/held-out split, goal, horizon, actions, statistics, and comparators remain fixed across the entire curve.

For every scalar field in `NucleationConfig`, except `width`, `height`, and `seed`, interpolate linearly:

`value(lambda) = easy_value + lambda * (hard_value - easy_value)`

The easy endpoint is the Experiment 002/default transition law:

- `spontaneous_rate=0.02`
- `nucleation_drive_gain=0.18`
- `frontier_base=0.08`
- `frontier_neighbor_gain=0.75`
- `frontier_drive_gain=0.18`
- `commit_base=0.25`
- `commit_neighbor_gain=0.35`
- `commit_drive_gain=0.35`
- `barrier=0.10`

The hard endpoint is the frozen Experiment 006 law:

- `spontaneous_rate=0.002`
- `nucleation_drive_gain=0.18`
- `frontier_base=0.03`
- `frontier_neighbor_gain=0.50`
- `frontier_drive_gain=0.12`
- `commit_base=0.14`
- `commit_neighbor_gain=0.30`
- `commit_drive_gain=0.25`
- `barrier=0.16`

No endpoint or interpolation value may be changed after the first Experiment 007 matrix execution.

## Frozen task boundary

- reference state: pinned Experiment 002 `77/81` ordered state;
- recovery goal: ordered fraction `>= 0.90`;
- recovery horizon: `9` ticks;
- lattice: `9 x 9`;
- action set: unchanged `RECOVERY_ACTIONS` from Experiment 004;
- controller state representation: unchanged coarse `(ordered, metastable, frontier)` bins;
- learner: unchanged tabular Q-learning algorithm.

## Frozen training boundary

At **each lambda independently**, train one fresh policy using the same six training damage geometries defined by Experiment 006 and training seeds:

`109, 113, 127, 131, 137, 139`

This yields `6 geometries x 6 seeds = 36` training cases per lambda.

Training settings at every lambda:

- episodes: `2400`;
- max steps: `9`;
- goal fraction: `0.90`;
- training seed: `7007 + int(lambda * 100)`;
- `alpha=0.20`;
- `gamma=0.90`;
- `initial_epsilon=0.35`;
- `minimum_epsilon=0.03`;
- `effort_penalty=0.35`.

No held-out geometry or held-out recovery seed may be added to training.

## Frozen held-out matrix

At every lambda evaluate the same eight held-out damage geometries defined by Experiment 006:

- `center_6x6`
- `wide_cross`
- `double_vertical`
- `double_horizontal`
- `hollow_7x7`
- `thick_diagonal`
- `corner_blocks`
- `central_plus_ring`

Held-out recovery seeds:

`149, 151, 157, 163, 167, 173, 179, 181`

Therefore each lambda contains `8 geometries x 8 seeds = 64` held-out cases for learned/cooperative/brute-force controls.

## Frozen comparators

For each case evaluate:

1. `learned`: greedy policy trained at the same lambda;
2. `cooperative`: two `renucleate` actions followed by seven `cooperate` actions;
3. `brute_force`: nine `brute` actions;
4. `random`: 8 deterministic random schedules of length 9 sampled uniformly from the same action set.

Random schedule seeds are `707000 + lambda_index * 100000 + case_index * 100 + replicate_index`.

This produces `64 x 8 = 512` random runs per lambda and `3072` random runs across all six lambda values.

Every strategy stops accumulating declared control effort when it first crosses the recovery goal.

## Frozen metrics

At each lambda report for every strategy:

- success rate by tick 9;
- 95% Wilson success interval;
- median effort-to-goal among successful runs;
- median goal tick among successful runs;
- replay failures.

The declared effort score is algorithmic and dimensionless. It is **not physical energy**.

## Frozen controllability-boundary metric

For each strategy define:

`lambda50 = maximum tested lambda with success_rate >= 0.50`

If no tested lambda reaches 50% success, `lambda50 = NONE`.

For random control, success rate is computed over all 512 random schedules at that lambda.

The grid spacing is `0.20`; no interpolation between lambda points is permitted for the preregistered pass/fail label.

## Preregistered interpretation boundary

Return `CONTROLLABILITY_BOUNDARY_SHIFT_SIGNAL` only if all are true:

1. learned replay failures are zero at every lambda;
2. learned has a defined `lambda50`;
3. learned `lambda50` is at least `0.20` greater than cooperative `lambda50`;
4. learned `lambda50` is at least `0.20` greater than random `lambda50`;
5. there exists at least one tested lambda where learned success is `>= 0.50` while both cooperative and random success are `< 0.50`.

Return `CONTROLLABILITY_BOUNDARY_OVERLAP` if learned has a defined `lambda50` but the shift criteria above are not met.

Return `CONTROLLABILITY_BOUNDARY_NOT_FOUND` if learned never reaches 50% success at any tested lambda.

Brute force is reported as a reference but is not part of the shift pass/fail rule.

The result label and thresholds must not be changed after the first matrix execution.

## Evidence integrity

CI must fail for protocol/evidence violations such as:

- wrong lambda grid;
- wrong train or held-out case counts;
- wrong random-run count;
- train/held-out seed overlap;
- replay divergence;
- endpoint interpolation mismatch.

CI must **not** fail merely because the scientific result is negative or overlapping.

## Non-claims

Even a positive boundary-shift result would remain a bounded software observation. It would not establish that an AI can shift a real material phase boundary or recover a physical material. The physical hypothesis requires a declared experimental platform and measured calibration.