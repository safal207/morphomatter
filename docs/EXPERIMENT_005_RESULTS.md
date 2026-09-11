# Experiment 005 — preregistered generalization results

Preregistration commit: `fb1ae4e9892695b2f4760c50e3db0548546e9f23`

Matrix runner/CI head: `e01776e55285ae4b56e67db3e76524d973e0342f`

GitHub Actions run: `34525660439`

## Frozen evaluation surface

The preregistered matrix contains 8 held-out damage geometries crossed with 8 held-out recovery seeds, for 64 held-out cases. None of the held-out recovery seeds appears in training. Random control uses 16 deterministic schedules per held-out case, for 1024 random runs.

Ordered sites removed by geometry from the Experiment 002 reference state:

- `center_5x5`: 25
- `cross`: 13
- `diagonal_band`: 19
- `hollow_box`: 16
- `horizontal_band`: 14
- `l_shape`: 10
- `two_islands`: 18
- `vertical_band`: 14

## Exact CI result

| Strategy | Success | 95% Wilson CI | Median effort to goal | 95% bootstrap CI | Median goal tick | 95% bootstrap CI | Replay failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| learned | 64/64 = 1.000 | [0.943, 1.000] | **0.470** | [0.460, 0.560] | 4 | [4, 5] | 0 |
| cooperative | 64/64 = 1.000 | [0.943, 1.000] | 1.520 | [1.520, 1.520] | 4 | [4, 4] | 0 |
| brute-force | 61/64 = 0.953 | [0.871, 0.984] | 6.440 | [6.440, 7.360] | 7 | [7, 8] | 0 |
| random (16×64) | 1024/1024 = 1.000 | [0.996, 1.000] | 1.715 | [1.650, 1.788] | 4 | [4, 4] | 0 |

Paired cooperative-minus-learned effort advantage on the 64 jointly successful cases:

- median difference: `0.965`
- 95% bootstrap CI: `[0.960, 1.060]`

Preregistered outcome: `BOUNDED_GENERALIZATION_SIGNAL`.

## Interpretation

The preregistered criteria passed. Within this toy model and action space, the learned policy generalizes its **lower-control-effort** behavior across the frozen 64-case held-out matrix. The paired effort advantage remains strictly positive under the preregistered bootstrap interval.

However, the success-rate axis is saturated: all 1024 random schedules also reached the 90% goal within 12 ticks. Therefore Experiment 005 does **not** support the claim that the learned policy is uniquely capable of recovery, nor that learning improves success probability in this regime. The useful signal is narrower: the learned condition-selection policy reaches an easy recovery target with substantially lower declared actuation than the fixed cooperative and random baselines.

This saturation is itself a useful negative/limiting result. The next evaluation should make recovery materially harder before increasing model complexity—for example by lowering direct drive, reducing spontaneous nucleation, increasing barriers, introducing larger/disconnected damage, shortening the horizon, or changing the transition law between training and evaluation.

## Non-claims

These results do not establish physical programmable matter, physical self-repair, calibrated kinetics, physical energy savings, real-world AI control, or general AI superiority. The effort metric is dimensionless and algorithmic.
