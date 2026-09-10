# Experiment 004 — Learned Recovery on Held-Out Damage

## Question

Can a policy learned only from simulated recovery cases choose a lower-control-effort condition trajectory on an unseen damage pattern and unseen stochastic seed than fixed conventional baselines?

## Scope

This is a **simulation-only machine-learning experiment** over the dimensionless MorphoMatter toy model. It is not evidence of physical AI-controlled matter, physical self-healing, calibrated energy efficiency, or real-world generalization.

The learner is intentionally small: tabular Q-learning over three coarse state features:

- ordered fraction;
- metastable fraction;
- active frontier fraction.

Its action space contains five global condition settings: `renucleate`, `cooperate`, `balanced`, `brute`, and `hold`. It never commands individual sites.

## Training boundary

The pinned Experiment 002 state (`77/81` ordered) is used as the pre-damage reference.

Training uses four rectangular damage geometries:

- `3×4` at `(top=1, left=1)`;
- `4×3` at `(top=1, left=4)`;
- `3×5` at `(top=3, left=1)`;
- `3×4` at `(top=4, left=3)`.

Each geometry is paired with recovery seeds `3, 7, 11, 19, 23`, producing 20 declared training cases. Training uses 1200 episodes and deterministic training seed `2026`.

The reward is dimensionless and declared in code. It rewards increases in ordered fraction, gives smaller credit for metastable progress, penalizes declared control effort, and adds a terminal bonus for reaching 90% ordered.

## Held-out evaluation

The test case is not among the training geometries:

- damage: central `5×5` rectangle at `(top=2, left=2)`;
- exactly `25` ordered sites are removed from the pinned reference state;
- recovery seed: `37`, absent from training;
- horizon: at most 12 ticks;
- goal: at least `90%` ordered.

The learned policy is compared against:

1. the fixed cooperative heuristic from Experiment 003 (`2× renucleate + 10× cooperate`);
2. brute-force high drive (`12× brute`);
3. 32 deterministic random action schedules.

For fair control-effort comparison, each strategy stops accumulating effort once it first reaches the 90% goal.

## Acceptance boundary

The pinned held-out run must:

- reach at least 90% ordered within 12 ticks;
- replay exactly from the held-out damaged state;
- use less declared control effort to reach the goal than the fixed cooperative heuristic;
- use less declared control effort than the brute-force baseline;
- use less declared control effort than the median of the 32 random schedules.

It is **not required** to be faster than every baseline or to dominate every random draw. This prevents a selective claim from one lucky random schedule.

## Interpretation

Passing this experiment would establish only a bounded software result: a small learned controller can exploit state-dependent transition conditions on one held-out toy-model case more economically under the declared algorithmic cost than the selected baselines.

It would not establish that AI is necessary, that this policy is optimal, that the result transfers to physical matter, or that the declared cost corresponds to energy. The next credible step after this experiment is cross-seed/cross-damage evaluation with confidence intervals, followed by calibration to a declared physical platform.
