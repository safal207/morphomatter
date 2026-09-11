# Experiment 009 — preregistered action-space ablation

Status: **PREREGISTERED BEFORE FIRST EXPERIMENT 009 RESULT**

## Question

Experiment 008 showed that a richer learned observation reduced declared control effort but did not move the 50% controllability boundary beyond `lambda50 = 0.80`.

Experiment 009 asks a narrower causal question:

> Holding the rich observation, transition law, boundary grid, training/held-out cases, reward, Q-learning hyperparameters, training budget, goal, and horizon fixed, does a richer vocabulary of **global condition actions** move the learned controllability boundary?

This is a synthetic software ablation. It is not a physical material-control claim.

## Frozen boundary protocol

Reuse Experiment 008 / Experiment 007 exactly:

- lambda grid: `0.00, 0.20, 0.40, 0.60, 0.80, 1.00`;
- transition law: linear interpolation between the same easy and hard endpoint `NucleationConfig` values;
- 9×9 Experiment 002 reference state;
- the same six training damage geometries;
- training seeds: `109, 113, 127, 131, 137, 139`;
- the same eight held-out damage geometries;
- held-out seeds: `149, 151, 157, 163, 167, 173, 179, 181`;
- 36 training cases and 64 held-out cases per lambda;
- goal ordered fraction: `0.90`;
- recovery horizon: `9` ticks;
- Q-learning episodes: `2400` per lambda;
- `alpha=0.20`, `gamma=0.90`;
- epsilon schedule: `0.35` to floor `0.03`;
- effort penalty: `0.35`;
- rich-state encoder exactly as frozen in Experiment 008;
- exact transition replay required.

The Experiment 008 original-rich curve must reproduce before the expanded-action result is interpreted.

## Frozen original action set

The original five global actions remain exactly:

| Action | drive | coupling_scale | threshold_scale |
|---|---:|---:|---:|
| `renucleate` | `0.55` | `1.00` | `0.80` |
| `cooperate` | `0.12` | `1.50` | `0.80` |
| `balanced` | `0.25` | `1.25` | `0.80` |
| `brute` | `0.80` | `0.00` | `0.80` |
| `hold` | `0.02` | `1.50` | `0.80` |

## Frozen expanded action set

The expanded learner receives those same five actions plus **six** additional global actions:

| New action | drive | coupling_scale | threshold_scale | Purpose |
|---|---:|---:|---:|---|
| `couple_gentle` | `0.08` | `1.80` | `0.80` | stronger coupling with less direct drive |
| `couple_strong` | `0.18` | `1.80` | `0.80` | stronger coupling with moderate drive |
| `bridge_drive` | `0.38` | `1.20` | `0.80` | intermediate drive between balanced and renucleate |
| `cooperate_low_threshold` | `0.12` | `1.50` | `0.70` | same cooperative drive/coupling with lower threshold scale |
| `renucleate_low_threshold` | `0.55` | `1.00` | `0.70` | same renucleation drive/coupling with lower threshold scale |
| `stabilize_high_threshold` | `0.08` | `1.50` | `0.90` | low-drive higher-threshold stabilization option |

The expanded action map therefore has exactly `11` actions. All are global conditions. No action targets an individual site, damage geometry, coordinate, seed, or future stochastic draw.

No new action may be added, removed, or altered after the first Experiment 009 run starts.

## Frozen learner comparison

At every lambda train two rich-state learners from scratch:

1. `rich_original`: Experiment 008 rich-state learner with the original five actions;
2. `rich_expanded`: the same learner and hyperparameters with the frozen 11-action set above.

Use the same training cases and the same per-lambda training seed for both learners:

`9009 + int(lambda * 100)`.

Changing the action map is the intended experimental variable. The rich state encoder, reward, horizon, transition law, cases, and training budget remain fixed.

Also reproduce the fixed cooperative heuristic from Experiment 007 as the capability reference.

## Frozen metrics

For each lambda and learner report:

- success count and rate across 64 held-out cases;
- 95% Wilson success interval;
- median declared control effort among successes;
- median tick to goal among successes;
- action counts;
- replay failures.

Primary boundary metric:

`lambda50 = largest tested lambda with observed success rate >= 0.50`.

## Preregistered interpretation boundary

Return `EXPANDED_ACTION_CAPABILITY_SHIFT` only if all are true:

1. `rich_expanded lambda50 >= rich_original lambda50 + 0.20`;
2. `rich_expanded lambda50 > cooperative lambda50`;
3. all expanded-policy held-out traces replay exactly;
4. at least one preregistered lambda has expanded success `>= 0.50` while both original-rich and cooperative success are `< 0.50`.

Because Experiment 008 froze both original-rich and cooperative `lambda50` at `0.80`, this requires the expanded learner to reach `lambda50 = 1.00` on the frozen grid.

If the capability boundary does not move but, at the shared highest passing lambda, expanded-rich has the same-or-higher success count than original-rich and lower median declared effort, report `EXPANDED_ACTION_EFFORT_ONLY`.

Otherwise report `EXPANDED_ACTION_NO_GAIN_OR_MIXED`.

Scientific failure or overlap must be preserved as a result and must not itself fail CI. CI should fail only for protocol/evidence integrity violations.

## Non-claims

A positive result would not establish:

- physical programmable matter;
- a real phase boundary;
- physical energy savings;
- general superiority of reinforcement learning;
- optimality of this hand-designed action set.

A negative result would reject only this frozen 11-action / rich-state / tabular-Q test under the synthetic transition model and fixed training budget.