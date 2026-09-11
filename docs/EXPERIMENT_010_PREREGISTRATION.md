# Experiment 010 — preregistered bounded continuous MPC reachability probe

Status: **PREREGISTERED BEFORE FIRST EXPERIMENT 010 RESULT**

## Question

Does replacing the tabular learned controller with a finite-budget model-predictive planner over **continuous bounded global conditions** move the 50% controllability boundary beyond the frozen Experiment 007–009 value `lambda50 = 0.80`?

This is a software reachability probe inside the existing synthetic transition surrogate. It is not a physical-material claim.

## Frozen causal boundary

Experiment 010 keeps fixed from Experiments 007–009:

- transition surrogate and interpolation law;
- lambda grid `0.00, 0.20, 0.40, 0.60, 0.80, 1.00`;
- Experiment 006 training/held-out geometry definitions (no new held-out geometry is introduced);
- held-out recovery seeds `149, 151, 157, 163, 167, 173, 179, 181`;
- 8 held-out geometries × 8 seeds = 64 cases per lambda;
- recovery goal `>= 0.90` ordered;
- maximum executed recovery horizon `9` ticks;
- declared control-effort function;
- one-way `DISORDERED -> METASTABLE -> ORDERED` transition law;
- deterministic transition replay requirement.

The frozen Experiment 009 comparator boundary is:

- expanded-rich discrete policy `lambda50 = 0.80`;
- original-rich policy `lambda50 = 0.80`;
- cooperative heuristic `lambda50 = 0.80`.

The frozen Experiment 009 expanded success counts are:

`(49, 45, 42, 40, 35, 19)`

for the lambda grid above.

## Planner access — intentionally strong

The planner is deliberately given stronger model access than the learned policies. At each decision it may use:

- the complete current 9×9 phase state;
- the current logical tick;
- the exact frozen `NucleationConfig` for the current lambda;
- the material stochastic seed;
- the exact deterministic synthetic transition function.

Because the current surrogate is Markov in `(state, tick, config, seed)`, candidate futures may be simulated exactly inside the software model.

This makes Experiment 010 an **upper-bound-style software reachability probe**, not a realistic sensing/control architecture. No claim should be made that a physical controller would know future stochastic outcomes this way.

## Frozen continuous control box

Each planner action is one global `Conditions` triple sampled continuously from the rectangular box:

- `drive` in `[0.02, 0.80]`;
- `coupling_scale` in `[0.00, 1.80]`;
- `threshold_scale` in `[0.70, 0.90]`.

These bounds are exactly the component-wise min/max envelope of the frozen Experiment 009 expanded discrete global action vocabulary. Experiment 010 may use new **combinations and continuous values inside this envelope**, but it may not exceed the envelope and may not target any site, coordinate, damage geometry, or case label.

## Frozen MPC / CEM budget

At each executed recovery tick:

1. Set lookahead horizon to `min(3, remaining recovery ticks)`.
2. Optimize a continuous condition schedule of that lookahead length with a deterministic cross-entropy-style search.
3. Use exactly `3` search iterations.
4. Use exactly `48` candidate schedules per iteration.
5. Retain exactly the top `8` candidates as elites after each iteration.
6. Iteration 1 samples every action component independently and uniformly inside the frozen bounds.
7. Iterations 2–3 sample each component from a Gaussian fitted independently to the elites from the previous iteration, clipped to the frozen bounds.
8. The per-component standard deviation floor is `10%` of that component's full frozen range.
9. After iteration 3, execute **only the first action** of the best final candidate, observe the resulting state, and replan.
10. Stop execution immediately after the recovery goal is reached or after 9 executed ticks.

Planner sampling RNG is independent from the material stochastic seed and is frozen as:

`1_010_000 + lambda_index * 100_000 + case_index * 1_000 + current_tick`

where `lambda_index` is the zero-based index in the frozen lambda grid, `case_index` is the zero-based held-out case index in geometry-major / seed-minor order, and `current_tick` is the current executed recovery tick before replanning.

## Frozen candidate ranking

Candidate schedules are ranked lexicographically by:

1. whether the recovery goal is reached within the candidate lookahead (`True` first);
2. earlier candidate-relative goal step if the goal is reached;
3. larger final ordered fraction;
4. larger final metastable fraction;
5. lower declared control effort over the candidate schedule.

No post-result weight tuning is permitted.

## Frozen metrics

For each lambda report:

- planner successes out of 64;
- Wilson 95% interval for planner success rate;
- planner median tick-to-goal among successful runs;
- planner median declared control effort among successful runs;
- planner replay failures;
- frozen Experiment 009 expanded-rich success count for reference;
- frozen cooperative success count for reference.

Primary boundary metric:

`lambda50 = largest tested lambda with observed success >= 0.50`.

## Preregistered interpretation

Return `CONTINUOUS_MPC_BOUNDARY_SHIFT` only if all are true:

1. planner replay failures are zero;
2. planner `lambda50 = 1.00`;
3. planner `lambda50` is at least one full lambda-grid step above expanded-rich (`0.80`);
4. planner `lambda50` is at least one full lambda-grid step above cooperative (`0.80`);
5. at `lambda = 1.00`, planner success is at least `32/64` while frozen expanded-rich and cooperative are both below `32/64`.

If the boundary does not shift, return `CONTINUOUS_MPC_EFFORT_ONLY` only if:

- planner `lambda50 = 0.80`;
- planner success at `lambda = 0.80` is at least the frozen expanded-rich `35/64`;
- planner median declared effort at `lambda = 0.80` is strictly below frozen expanded-rich median effort `1.700`;
- replay failures are zero.

Otherwise return `CONTINUOUS_MPC_NO_GAIN_OR_MIXED`.

The thresholds and labels must not be changed after observing Experiment 010 results.

## Evidence integrity

CI must fail on:

- lambda-grid drift;
- held-out case-count drift;
- continuous-bound drift;
- planner-budget drift;
- comparator-count drift from the frozen Experiment 009 values;
- any planner replay failure.

A negative scientific result is **not** a CI failure.

## Non-claims

Even `CONTINUOUS_MPC_BOUNDARY_SHIFT` would not establish physical programmable matter, physical energy savings, general AI superiority, or a real phase boundary.

If the planner does **not** shift the boundary, that does not mathematically prove the current global-control surrogate is unreachable above `lambda = 0.80`: the optimizer has a finite stochastic search budget and only a 3-step receding lookahead. A negative result would instead strengthen the bounded hypothesis that the observed ceiling is not explained merely by tabular policy class or discrete action quantization within the tested control envelope.
