# MorphoMatter

**Goal-programmable matter research sandbox.**

> Don't command the particles. Create the conditions in which the desired transition becomes likely.

MorphoMatter explores whether a controller can steer a population of simple interacting elements by changing **environmental conditions**, rather than micromanaging individual elements.

## Core hypothesis

```text
goal
  ↓
controller
  ↓
condition schedule
  ↓
local interactions + transition thresholds
  ↓
self-organization
  ↓
observed state + transition trace
  └──────────── feedback ────────────┘
```

The first software model is intentionally **dimensionless**. It is not a calibrated model of crystallization, magnetic colloids, water, or any specific material.

## Why COSMIC-ORGANICS matters

The sibling COSMIC-ORGANICS project already contains useful algorithmic patterns: explicit transition states, local coupling, thresholds, path-gradient feedback, sparse active frontiers, and separately checkable transition traces. MorphoMatter reuses those ideas as research abstractions without claiming that COSMIC is a law of physics.

See [`docs/COSMIC_BRIDGE.md`](docs/COSMIC_BRIDGE.md).

## Experiment 001 — transition-condition map

The first milestone is deliberately small:

1. Start with a disordered 2D lattice.
2. Apply only global/dimensionless transition conditions.
3. Cross `DISORDERED → METASTABLE → ORDERED` without commanding sites individually.
4. Record every completed transition.
5. Replay the trace and verify the final state.
6. Use a conventional path-gradient controller as the baseline that any future AI controller must beat.

### Transition Map Explorer

`TransitionMapExplorer` separates two questions that should not be conflated:

- **phase-map scan**: hold one condition point for a declared number of steps and record the resulting organization score, dominant phase, ordered fraction and transition count;
- **schedule search**: search a bounded sequence of condition points for a low-declared-cost route to a target organization score.

The v0 search is intentionally fail-closed when `memory_decay != 0`. With hidden path memory, phase labels alone are not a sufficient search state.

Run the example:

```bash
PYTHONPATH=src python experiments/transition_map.py
```

The example scans a 45-point dimensionless condition grid around a seeded 5×5 lattice and then searches for a schedule reaching organization score `>= 0.90`.

## Experiment 002 — nucleation and moving frontier

Experiment 002 asks a stronger question: can global conditions make **rare nuclei** appear and then let **local coupling** carry an ordering frontier through the lattice?

The pinned toy schedule uses two stages:

```text
stage 1: higher direct drive → rare nucleation
stage 2: lower direct drive + stronger local coupling → frontier propagation
```

The seeded model records `nucleation`, `frontier_growth`, and `commit` events with transition probability, deterministic pseudo-random draw, local neighbor order, and the conditions used for each step. The trace must replay exactly.

Run it:

```bash
PYTHONPATH=src python experiments/nucleation_frontier.py
```

The pinned seed reaches `77/81` ordered sites (`0.950617`) at tick 24. The reference trace contains `6` nucleation, `74` frontier-growth, and `77` commit events. These are reproducible algorithmic observations, **not physical crystallization measurements**.

See [`docs/EXPERIMENT_002_NUCLEATION.md`](docs/EXPERIMENT_002_NUCLEATION.md).

## Experiment 003 — damage and recovery controls

Experiment 003 rebuilds the pinned Experiment 002 state, destroys a fixed central region, then compares three recovery strategies on the **same damaged state and same deterministic stochastic surface**:

```text
A. brief renucleation + low drive + strong local coupling
B. same renucleation pulse + low drive + no coupling
C. high direct drive + no coupling
```

The pinned damage removes exactly `20` ordered sites, dropping the reference from `77/81` ordered to `57/81` ordered.

Under recovery seed `11` and the declared 12-tick schedules:

| Strategy | Final ordered | First tick ≥90% | Declared control effort |
|---|---:|---:|---:|
| cooperative coupling | `81/81` (`1.000000`) | `5` | `3.040` |
| no coupling | `73/81` (`0.901235`) | `12` | `3.540` |
| brute-force high drive | `80/81` (`0.987654`) | `7` | `11.040` |

The cooperative recovery contains renucleation, frontier-growth, and commit events and replays exactly from the damaged state. The control-effort score is a dimensionless algorithmic baseline, **not physical energy**.

Run it:

```bash
PYTHONPATH=src python experiments/damage_recovery.py
```

See [`docs/EXPERIMENT_003_DAMAGE_RECOVERY.md`](docs/EXPERIMENT_003_DAMAGE_RECOVERY.md).

## Experiment 004 — learned recovery on held-out damage

Experiment 004 removes the hand-written recovery schedule from the central comparison. A minimal **tabular Q-learning** controller trains on 20 declared simulated cases: four rectangular damage geometries crossed with five recovery seeds. It observes only coarse global state features—ordered fraction, metastable fraction, and active-frontier fraction—and selects among five global condition settings.

The held-out case is a different central `5×5` damage geometry with recovery seed `37`, neither of which appears in training. The learner is compared against the fixed cooperative heuristic, brute-force high drive, and 32 deterministic random schedules. Effort is accumulated only until each strategy first crosses the `90%` recovery goal.

The held-out learned path was `cooperate → cooperate → cooperate → hold → hold → hold`, reaching `0.925926` ordered at tick `6` with declared effort `0.840`, versus `1.900` for the fixed cooperative heuristic at the same tick.

See [`docs/EXPERIMENT_004_LEARNED_RECOVERY.md`](docs/EXPERIMENT_004_LEARNED_RECOVERY.md).

## Experiment 005 — preregistered generalization matrix

Experiment 005 freezes the evaluation surface **before execution** and tests the same learned policy over `8` unseen damage geometries × `8` unseen recovery seeds = `64` held-out cases. Random control uses 16 deterministic schedules per case (`1024` runs total).

Preregistration: [`docs/EXPERIMENT_005_PREREGISTRATION.md`](docs/EXPERIMENT_005_PREREGISTRATION.md).

Exact CI result:

| Strategy | Success | Median effort to goal | Median goal tick |
|---|---:|---:|---:|
| learned | `64/64` | **`0.470`** | `4` |
| cooperative | `64/64` | `1.520` | `4` |
| brute-force | `61/64` | `6.440` | `7` |
| random (16×64) | `1024/1024` | `1.715` | `4` |

The preregistered paired median effort advantage `(cooperative - learned)` is `0.965`, with 95% bootstrap interval `[0.960, 1.060]`. The frozen interpretation boundary returns `BOUNDED_GENERALIZATION_SIGNAL`.

The crucial limitation is that **all 1024 random schedules also succeed**. Success is saturated in this toy regime. Experiment 005 therefore supports only the narrower statement that the learned policy generalizes **lower declared control effort** across the frozen software matrix. It does **not** show unique recovery capability, higher success probability, physical energy savings, or general AI superiority.

Full result: [`docs/EXPERIMENT_005_RESULTS.md`](docs/EXPERIMENT_005_RESULTS.md).

Run it:

```bash
PYTHONPATH=src python experiments/generalization_matrix.py
```

## Experiment 006 — preregistered hard transition regime

Experiment 006 deliberately makes recovery harder to test whether learned control gains **capability**, not only lower control effort. Before the first run it froze:

- lower spontaneous nucleation;
- a higher transition barrier;
- larger held-out damage geometries removing `22–36` ordered sites;
- a stricter `>= 0.92` recovery goal;
- only `7` recovery ticks;
- `8` unseen geometries × `8` unseen seeds = `64` cases;
- `1024` random schedules as a pooled random baseline.

Preregistration: [`docs/EXPERIMENT_006_PREREGISTRATION.md`](docs/EXPERIMENT_006_PREREGISTRATION.md). Deterministic statistical/random seeds were frozen before execution in [`docs/EXPERIMENT_006_PREREGISTRATION_ADDENDUM.md`](docs/EXPERIMENT_006_PREREGISTRATION_ADDENDUM.md).

The first frozen hard-regime result is negative:

| Strategy | Success | 95% Wilson interval |
|---|---:|---:|
| learned | `0/64` | `[0.000, 0.057]` |
| cooperative | `0/64` | `[0.000, 0.057]` |
| brute-force | `0/64` | `[0.000, 0.057]` |
| random | `0/1024` | `[0.000, 0.004]` |

All transition traces replayed exactly. The frozen interpretation is:

`HARD_REGIME_MIXED_OR_NEGATIVE`

Experiment 006 therefore does **not** show learned recovery capability. Instead, it identifies an upper software boundary: this exact barrier/rate/damage/horizon combination is too severe for every declared strategy in the current model/action space. The protocol is not retuned after observing the failure; any intermediate-difficulty boundary search must be a new experiment number.

Full result: [`docs/EXPERIMENT_006_RESULTS.md`](docs/EXPERIMENT_006_RESULTS.md).

Run it:

```bash
PYTHONPATH=src python experiments/hard_transition_regime.py
```

## Verify

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python experiments/nucleation_frontier.py
PYTHONPATH=src python experiments/damage_recovery.py
PYTHONPATH=src python experiments/learned_recovery.py
PYTHONPATH=src python experiments/generalization_matrix.py
PYTHONPATH=src python experiments/hard_transition_regime.py
```

## Non-claims

This repository does not yet establish:

- a physical programmable material;
- nanoscale robots;
- a calibrated phase diagram;
- AI superiority over conventional control in physical systems;
- physical self-repair;
- physical energy, speed, or scaling advantages.

The explorer, recovery, and learned-policy cost metrics are declared algorithmic baselines, **not physical energy**. Experiments 004–006 are bounded software ML results only. Experiment 006 is a preserved negative result, not a physical limit.
