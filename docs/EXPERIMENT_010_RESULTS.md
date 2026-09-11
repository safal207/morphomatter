# Experiment 010 — bounded continuous MPC reachability probe results

## Provenance

Preregistration was committed before the first Experiment 010 result:

`6b27c651b665432dfd76ca0cca48f0606e6c71d4`

The first completed Experiment 010 implementation head was:

`db9cf2d22284d1885d6117eb49939a7c0e8fef64`

GitHub Actions push run:

`34574077199`

The run passed `34` unit tests and Experiments 002–010. The Experiment 009 expanded-rich comparator was retrained and reevaluated inside Experiment 010 and reproduced the frozen Experiment 009 success counts exactly before the MPC result was interpreted.

## Frozen result

Preregistered label:

`CONTINUOUS_MPC_BOUNDARY_SHIFT`

The bounded continuous model-predictive planner moved the observed 50% controllability boundary from `lambda50 = 0.80` to `lambda50 = 1.00`.

| Controller | lambda50 |
|---|---:|
| continuous MPC | **`1.00`** |
| expanded-rich tabular policy | `0.80` |
| cooperative heuristic | `0.80` |

At the hard endpoint `lambda = 1.00`:

- continuous MPC: `44/64` successes (`68.75%`), Wilson 95% CI `[0.566, 0.788]`;
- expanded-rich tabular policy: `19/64` (`29.69%`);
- cooperative heuristic: `16/64` (`25.00%`).

The preregistered hard-endpoint separation criterion (`>=32/64` for MPC while both comparators remain below `32/64`) therefore passed.

## Full success curve

| lambda | Continuous MPC | Expanded rich | Frozen cooperative |
|---:|---:|---:|---:|
| `0.00` | `64/64` (`100.0%`) | `49/64` (`76.6%`) | `57/64` (`89.1%`) |
| `0.20` | `64/64` (`100.0%`) | `45/64` (`70.3%`) | `49/64` (`76.6%`) |
| `0.40` | `64/64` (`100.0%`) | `42/64` (`65.6%`) | `42/64` (`65.6%`) |
| `0.60` | `59/64` (`92.2%`) | `40/64` (`62.5%`) | `38/64` (`59.4%`) |
| `0.80` | `57/64` (`89.1%`) | `35/64` (`54.7%`) | `33/64` (`51.6%`) |
| `1.00` | `44/64` (`68.8%`) | `19/64` (`29.7%`) | `16/64` (`25.0%`) |

All continuous-MPC replay failures: `0`.

## Effort and speed

The capability shift is not an efficiency win under the declared algorithmic effort metric.

| lambda | MPC median effort | MPC median goal tick | Expanded-rich median effort |
|---:|---:|---:|---:|
| `0.00` | `2.699` | `4.0` | `1.330` |
| `0.20` | `2.911` | `4.0` | `1.660` |
| `0.40` | `3.083` | `5.0` | `1.540` |
| `0.60` | `3.248` | `5.0` | `1.895` |
| `0.80` | `3.544` | `6.0` | `1.700` |
| `1.00` | `3.851` | `6.5` | `1.710` |

The MPC controller spends more declared control effort to achieve substantially greater reachability. Declared effort is dimensionless and is **not physical energy**.

## What changed relative to Experiments 008–009

The planner uses the same synthetic transition surrogate, lambda grid, damage geometries, held-out material seeds, recovery goal, 9-tick execution horizon, and the same component-wise control envelope as Experiment 009.

The continuous global control box was frozen to the Experiment 009 action-envelope extrema:

- `drive` in `[0.02, 0.80]`;
- `coupling_scale` in `[0.00, 1.80]`;
- `threshold_scale` in `[0.70, 0.90]`.

Unlike the tabular policies, the MPC probe has intentionally privileged access to the full current lattice state, logical tick, exact transition surrogate, and material stochastic seed. It uses a finite deterministic CEM-style search (`3` iterations × `48` candidate schedules, top `8` elites) with a 3-step receding lookahead.

## Interpretation

Within this synthetic model and frozen continuous control envelope, the Experiment 007–009 `lambda50 = 0.80` ceiling is **not a reachability limit of the surrogate itself**. A stronger model-based continuous planner finds successful schedules for a majority (`44/64`) of held-out cases even at `lambda = 1.00`.

This narrows the causal picture substantially:

1. richer observation alone improved effort but did not move the boundary (Experiment 008);
2. a modest larger discrete action vocabulary improved some success counts but did not move the boundary (Experiment 009);
3. continuous model-predictive search with exact surrogate access **did** move the boundary to the hardest tested lambda (Experiment 010).

However, Experiment 010 deliberately changes more than one controller property at once: it introduces both continuous-valued actions and exact model-predictive planning with privileged future-draw knowledge. Therefore it does **not** identify whether the shift is caused primarily by continuous action resolution, model-based planning, exact stochastic knowledge, or their combination.

The clean next causal test is a factorial controller ablation: run the same privileged MPC/search procedure over only the frozen 11-action discrete vocabulary and compare it against continuous MPC. If discrete MPC also shifts to `1.00`, planning/model access is sufficient; if discrete MPC stays at `0.80` while continuous MPC remains at `1.00`, continuous action resolution is implicated.

## Important limitations

- The planner knows the exact synthetic material seed and transition law.
- Candidate futures therefore use exact deterministic stochastic outcomes inside the toy model.
- The planner is not a deployable physical controller design.
- The CEM optimizer has finite search budget and 3-step lookahead.
- `44/64` at lambda `1.00` does not imply the remaining 20 cases are unreachable.
- The transition model is synthetic and dimensionless.
- Control effort is not physical energy.

## Non-claims

Experiment 010 does not establish physical programmable matter, a real material phase boundary, physical self-repair, physical energy savings, nanoscale robots, or general AI superiority.

The supported software claim is narrower: **inside the frozen synthetic surrogate, a bounded continuous model-predictive controller can reach target recovery states beyond the capability boundary observed for the tested tabular and heuristic controllers.**
