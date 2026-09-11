# Experiment 008 — preregistered rich-state causality test

Status: **PREREGISTERED BEFORE FIRST EXPERIMENT 008 RESULT**

## Question

Experiment 007 found the same 50% controllability boundary for the coarse learned policy and the fixed cooperative heuristic (`lambda50 = 0.80`). Does a richer observation of the *same simulated material state* shift the learned controllability boundary, while keeping the transition law, action set, learning rule, training budget, damage cases, stochastic seeds, goal, and horizon fixed?

This is a software representation ablation. It is not a physical-material claim.

## Frozen causal contrast

The only intended experimental change from the Experiment 007 learned controller is the state encoder.

### Coarse encoder

Reuse the Experiment 007 / Experiment 004 state exactly:

1. ordered fraction bin;
2. metastable fraction bin;
3. active-frontier fraction bin.

### Rich encoder

The rich encoder must contain the same three coarse features plus the following declared features derived only from the current lattice state and its already-recorded transition trace:

4. largest connected non-ordered component fraction;
5. number of connected non-ordered components, capped into a small categorical bin;
6. mean ordered-neighbor support across current frontier sites;
7. recent ordered-commit progress from the immediately preceding logical tick;
8. remaining recovery-horizon bucket.

No site coordinates, held-out geometry labels, held-out seed identifiers, future stochastic draws, target-case identity, or manually encoded damage-pattern names may enter the policy state.

## Frozen boundary protocol

Reuse the Experiment 007 protocol exactly:

- lambda grid: `0.00, 0.20, 0.40, 0.60, 0.80, 1.00`;
- easy endpoint: default Experiment 002 `NucleationConfig`;
- hard endpoint: Experiment 006 hard `NucleationConfig`;
- linear interpolation of the same nine transition-law fields;
- goal ordered fraction: `0.90`;
- maximum recovery horizon: `9` ticks;
- action set: unchanged `RECOVERY_ACTIONS` (`renucleate`, `cooperate`, `balanced`, `brute`, `hold`);
- Q-learning algorithm/reward: unchanged from Experiment 007;
- training episodes: `2400` per lambda;
- learning hyperparameters: `alpha=0.20`, `gamma=0.90`, `initial_epsilon=0.35`, `minimum_epsilon=0.03`, `effort_penalty=0.35`;
- six Experiment 007 training geometries;
- training seeds: `109, 113, 127, 131, 137, 139`;
- eight Experiment 007 held-out geometries;
- held-out seeds: `149, 151, 157, 163, 167, 173, 179, 181`;
- `64` held-out learned cases per lambda;
- fixed cooperative and brute-force schedules unchanged;
- random baseline: `8` deterministic schedules per held-out case (`512` runs per lambda), using the same deterministic schedule-seed construction as Experiment 007.

The coarse learner must also be rerun under the same implementation and seeds in Experiment 008. Its success curve is expected to reproduce the frozen Experiment 007 curve; material divergence must be reported rather than silently accepted.

## Frozen rich-learning seeds

To keep the two learning procedures deterministic but independent:

- coarse Q-learning seed at each lambda remains `7007 + int(lambda * 100)`;
- rich Q-learning seed at each lambda is `8008 + int(lambda * 100)`.

No held-out result may be used to select or change these seeds.

## Primary metric

For each learned policy, compute:

`lambda50 = largest tested lambda with held-out success rate >= 0.50`.

Use the Experiment 007 `NONE` semantics: `NONE` is below the minimum tested lambda; if the rich learner is `NONE`, a positive boundary shift is impossible.

## Preregistered interpretation boundary

Return `RICH_STATE_BOUNDARY_SHIFT` only if all are true:

1. rich-policy transition replay failures = `0` across all held-out runs;
2. rich `lambda50` is at least one full grid step (`0.20`) greater than coarse `lambda50`;
3. rich `lambda50` is at least one full grid step greater than fixed cooperative `lambda50`;
4. at at least one preregistered lambda, rich success is `>= 0.50` while both coarse and cooperative success are `< 0.50`.

Return `RICH_STATE_EFFORT_ONLY` if the boundary-shift criteria fail, but rich reaches the same `lambda50` as coarse/cooperative and has lower median declared control effort among successful runs at that shared boundary.

Otherwise return `RICH_STATE_NO_SHIFT_OR_MIXED`.

The interpretation thresholds must not be changed after observing Experiment 008.

## Secondary metrics

Report for every lambda:

- rich/coarse/cooperative/brute/random success rate;
- 95% Wilson success interval;
- median declared effort to goal among successful runs;
- median goal tick among successful runs;
- replay failures;
- rich and coarse action counts.

The declared effort score is algorithmic and dimensionless, not physical energy.

## Evidence-integrity requirements

CI may fail for implementation/protocol violations such as:

- changed lambda grid, seeds, case counts, action set, horizon, or goal;
- leaked held-out identifiers into policy state;
- replay divergence;
- endpoint interpolation mismatch;
- failure to reproduce the coarse Experiment 007 reference curve within exact integer success counts.

A scientifically negative result must not itself fail CI.

## Non-claims

Even a positive Experiment 008 result would not establish physical programmable matter, physical self-repair, real phase-boundary control, physical energy savings, or general AI superiority. It would only support the bounded software claim that additional observable state information improves controllability under this toy transition model.
