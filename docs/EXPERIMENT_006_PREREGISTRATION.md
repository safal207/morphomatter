# Experiment 006 — preregistered hard transition regime

Status: **PREREGISTERED BEFORE HARD-REGIME EXECUTION**

## Question

When recovery is made materially harder inside the software model—lower spontaneous nucleation, a higher transition barrier, larger damage, and a shorter recovery horizon—does a learned condition-selection policy improve **recovery capability**, not only declared control effort?

This is a simulation-only experiment. The rates, barriers, actions, effort score, and recovery dynamics are dimensionless algorithmic quantities. They are not calibrated physical material parameters or physical energy.

## Frozen reference state

Use the Experiment 002 reference state on the 9×9 lattice:

- assembly seed `26`;
- two nucleation-stage ticks followed by 22 propagation-stage ticks;
- expected reference ordered fraction `77/81`.

Damage is applied to that same reference state before each recovery case.

## Frozen hard recovery law

Every training and evaluation recovery rollout uses `NucleationConfig` with:

- `width=9`, `height=9`;
- `spontaneous_rate=0.002`;
- `nucleation_drive_gain=0.18`;
- `frontier_base=0.03`;
- `frontier_neighbor_gain=0.50`;
- `frontier_drive_gain=0.12`;
- `commit_base=0.14`;
- `commit_neighbor_gain=0.30`;
- `commit_drive_gain=0.25`;
- `barrier=0.16`;
- case-specific deterministic recovery seed.

The hard law is frozen before matrix execution.

## Frozen action set

Use the existing five global condition actions from `RECOVERY_ACTIONS` unchanged:

- `renucleate`;
- `cooperate`;
- `balanced`;
- `brute`;
- `hold`.

No per-site actions are allowed.

## Frozen training boundary

Train one tabular Q-learning policy only on the following six damage geometries:

1. rectangle rows `1..3`, columns `1..5`;
2. rectangle rows `1..5`, columns `5..7`;
3. horizontal band rows `5..6`, columns `1..7`;
4. off-center rectangle rows `3..6`, columns `1..4`;
5. L-shape: column `2`, rows `1..5`, union row `5`, columns `2..6`;
6. two 3×3 islands: rows `1..3`, cols `1..3`, union rows `5..7`, cols `5..7`.

Training recovery seeds:

`5, 13, 17, 61, 67, 71`

This yields `36` training cases. No held-out geometry or held-out recovery seed below may be added to training.

Training hyperparameters are frozen:

- episodes: `3000`;
- maximum recovery steps: `7`;
- goal ordered fraction: `0.92`;
- training RNG seed: `6006`;
- learning rate `alpha=0.20`;
- discount `gamma=0.90`;
- initial epsilon `0.35`;
- minimum epsilon `0.03`;
- effort penalty `0.35`.

## Frozen held-out hard matrix

Evaluate **8 unseen damage geometries × 8 unseen recovery seeds = 64 cases**.

Held-out recovery seeds:

`73, 79, 83, 89, 97, 101, 103, 107`

Held-out geometries:

1. `center_6x6`: rows `1..6`, columns `1..6`;
2. `wide_cross`: rows `3..5`, columns `1..7`, union columns `3..5`, rows `1..7`;
3. `double_vertical`: columns `1..2` and `6..7`, rows `1..7`;
4. `double_horizontal`: rows `1..2` and `6..7`, columns `1..7`;
5. `hollow_7x7`: perimeter of rows `1..7`, columns `1..7`;
6. `thick_diagonal`: cells `(r,c)` with `0 <= r,c <= 8` and `abs(r-c) <= 1`;
7. `corner_blocks`: 4×4 block at top-left union 4×4 block at bottom-right;
8. `central_plus_ring`: center 3×3 block union perimeter of rows `1..7`, columns `1..7`.

These definitions are frozen before execution.

## Frozen comparators

For each held-out case evaluate:

- `learned`: greedy hard-regime policy;
- `cooperative`: two `renucleate` actions followed by five `cooperate` actions;
- `brute_force`: seven `brute` actions;
- `random`: 16 deterministic uniformly sampled action schedules of length seven from the same five-action set.

All strategies stop accumulating effort once they first reach the goal.

## Frozen primary endpoint

A case is a **success** only if ordered fraction reaches at least `0.92` within `7` recovery ticks and the resulting transition trace replays exactly.

Primary metrics:

1. success rate;
2. declared effort to goal among successes;
3. tick to goal among successes;
4. replay failures.

Uncertainty summaries:

- success rate: 95% Wilson interval;
- median effort and goal tick: deterministic 95% percentile bootstrap interval, 2000 resamples;
- paired effort difference `(cooperative - learned)` on jointly successful cases: deterministic 95% percentile bootstrap interval of the median paired difference.

Random success is reported across all `64 × 16 = 1024` random schedules.

## Preregistered interpretation boundary

Return `HARD_REGIME_CAPABILITY_SIGNAL` only if **all** of the following hold:

1. learned success rate is at least `0.70` across the 64 held-out cases;
2. learned success rate exceeds cooperative success rate by at least `0.10` absolute;
3. learned success rate exceeds pooled random success rate by at least `0.10` absolute;
4. learned successful traces have zero replay failures.

Return `HARD_REGIME_EFFORT_ONLY` if capability criteria 2–3 fail, but:

- learned success rate is at least `0.70`;
- learned median effort is lower than cooperative median effort;
- the 95% bootstrap interval for paired median `(cooperative - learned)` effort has lower bound greater than zero.

Otherwise return `HARD_REGIME_MIXED_OR_NEGATIVE`.

The thresholds and labels above must not be changed after observing the first hard-regime matrix run. If the regime is too hard or too easy, that is itself a result; any redesigned regime must be a new experiment number.

## Non-claims

Even `HARD_REGIME_CAPABILITY_SIGNAL` would remain a bounded software result. It would not establish physical programmable matter, physical self-repair, calibrated transition kinetics, physical energy savings, nanoscale robots, or general AI superiority.
