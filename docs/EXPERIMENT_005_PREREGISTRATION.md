# Experiment 005 — preregistered generalization matrix

Status: **PREREGISTERED BEFORE MATRIX EXECUTION**

## Question

Does the Experiment 004 tabular recovery policy retain its low-effort recovery behavior across a fixed matrix of damage geometries and stochastic seeds that were not used for training?

This is a simulation-only evaluation. It is not evidence of physical self-healing, physical energy savings, or general AI superiority.

## Frozen training boundary

Use the same training surface as Experiment 004:

- four rectangular training damage patterns;
- recovery seeds `3, 7, 11, 19, 23`;
- 20 training cases total;
- 1200 deterministic Q-learning episodes;
- training seed `2026`;
- action set from `RECOVERY_ACTIONS`;
- goal ordered fraction `0.90`;
- maximum recovery horizon `12` ticks.

No held-out geometry or held-out recovery seed below may be added to training.

## Frozen held-out matrix

Evaluate the Cartesian product of **8 held-out damage geometries × 8 held-out recovery seeds = 64 cases**.

Held-out seeds:

`29, 31, 37, 41, 43, 47, 53, 59`

None appears in the Experiment 004 training seed set.

Held-out geometries on the 9×9 Experiment 002 reference state:

1. `center_5x5`: rows `2..6`, columns `2..6`.
2. `horizontal_band`: rows `3..4`, columns `1..7`.
3. `vertical_band`: rows `1..7`, columns `3..4`.
4. `cross`: center row `4`, columns `1..7`, union center column `4`, rows `1..7`.
5. `l_shape`: rows `1..6` at column `2`, union row `6`, columns `2..6`.
6. `two_islands`: rectangle rows `1..3`, columns `1..3`, union rectangle rows `5..7`, columns `5..7`.
7. `diagonal_band`: cells `(r,c)` with `1 <= r,c <= 7` and `abs(r-c) <= 1`.
8. `hollow_box`: perimeter of rows `2..6`, columns `2..6`.

These definitions are fixed before matrix execution.

## Frozen comparators

For every held-out case evaluate:

- `learned`: greedy Experiment 004 tabular policy;
- `cooperative`: two `renucleate` actions followed by ten `cooperate` actions;
- `brute_force`: twelve `brute` actions;
- `random`: 16 deterministic random schedules of length 12, sampled uniformly from the same five-action set. Random schedule seeds are derived only from the held-out case index and replicate index and do not affect material stochastic seeds.

Every strategy stops accumulating effort when it first reaches the `0.90` goal.

## Frozen metrics

Primary metrics:

1. success rate by tick 12;
2. declared control effort to goal among successful runs;
3. tick to goal among successful runs;
4. exact transition replay validity.

Uncertainty summaries:

- success rate: 95% Wilson interval;
- median effort and median goal tick: deterministic 95% percentile bootstrap interval with seed `5005` and 2000 resamples;
- paired effort advantage `cooperative effort - learned effort` on cases where both succeed: deterministic 95% percentile bootstrap interval of the median paired difference, seed `5006`, 2000 resamples.

The declared effort metric is algorithmic and dimensionless. It is **not physical energy**.

## Preregistered interpretation boundary

Experiment 005 supports a **bounded generalization signal** only if all of the following hold:

1. learned policy success rate is at least `0.90` across the 64 held-out cases;
2. every learned successful trace replays exactly;
3. learned median effort-to-goal is lower than cooperative median effort-to-goal;
4. the 95% bootstrap interval for the paired median effort advantage `(cooperative - learned)` has a lower bound strictly greater than `0`;
5. learned median effort-to-goal is lower than the median effort of successful random runs.

Brute force is retained as a reference comparator but is not part of the pass/fail boundary because its intentionally large actuation is expected to trade effort for robustness.

If any preregistered criterion fails, the result must be reported as a failed or mixed generalization result. The thresholds must not be changed after observing the matrix.

## Non-claims

Even a passing Experiment 005 would not establish:

- physical programmable matter;
- physical self-repair;
- calibrated phase-transition kinetics;
- physical energy savings;
- robustness outside this toy model/action space;
- superiority of AI in general.

The purpose is only to test whether the learned **condition-selection** behavior from Experiment 004 survives a larger frozen software evaluation surface.
