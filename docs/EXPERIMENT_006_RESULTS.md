# Experiment 006 — hard transition regime results

Status: **PREREGISTERED RESULT RECORDED WITHOUT RETUNING**

Preregistration commit: `fde8941eee5094cf7417baaa644c0d84a783c701`

Deterministic-seed addendum commit: `638e7a2f9dfee991682b05618f504749e8a362e8`

First hard-regime implementation/CI head: `597e28b48b0464c209176cbe0d0e5c2e9cccbdd2`

## Frozen hard matrix

The preregistered evaluation used:

- `8` unseen damage geometries × `8` unseen recovery seeds = `64` held-out cases;
- `16` random schedules per held-out case = `1024` random runs;
- recovery goal `>= 0.92` ordered fraction;
- maximum horizon `7` recovery ticks;
- the frozen hard transition law from the preregistration;
- the unchanged five-action global control set.

The held-out geometries removed between `22` and `36` ordered sites from the `77/81` Experiment 002 reference state.

## Exact first-run result

| Strategy | Success | 95% Wilson interval | Replay failures |
|---|---:|---:|---:|
| learned | `0/64` | `[0.000, 0.057]` | `0` |
| cooperative | `0/64` | `[0.000, 0.057]` | `0` |
| brute-force | `0/64` | `[0.000, 0.057]` | `0` |
| random | `0/1024` | `[0.000, 0.004]` | `0` |

No strategy reached the preregistered recovery endpoint, so effort-to-goal and goal-tick medians are undefined and no paired effort comparison is available.

The learned policy emitted the following aggregate greedy action counts across the 64 held-out rollouts:

- `cooperate`: `369`;
- `brute`: `63`;
- `hold`: `16`.

It selected no `renucleate` or `balanced` actions in these held-out rollouts, but that observation does not imply those actions are generally unnecessary; no rollout succeeded.

## Preregistered interpretation

`PREREGISTERED_RESULT=HARD_REGIME_MIXED_OR_NEGATIVE`

The capability criteria fail because learned success is `0`, below the frozen `0.70` minimum. The effort-only criteria are also inapplicable because there are no successful learned/cooperative pairs.

## Interpretation

Experiment 006 does **not** show learned recovery capability in the hard regime. It establishes a useful software boundary instead: the combination of the frozen barrier/rates, larger damage, `0.92` target, and seven-tick horizon is too severe for every declared strategy and baseline in the current model/action space.

This is not evidence that recovery is impossible. It is evidence only that **this exact preregistered regime is beyond the tested controllers under the frozen protocol**.

The correct next step is not to retune Experiment 006 after observing the failure. Any boundary-search or intermediate-difficulty regime must receive a new experiment number and its own preregistration.

## Non-claims

This negative software result does not establish physical limits, physical phase-transition barriers, physical self-repair limits, or general limits of AI. All quantities remain dimensionless and algorithmic.
