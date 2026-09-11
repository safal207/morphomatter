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

The software model is intentionally **dimensionless**. It is not a calibrated model of crystallization, magnetic colloids, water, or any specific material.

## Research path

- **Experiment 001** — transition-condition map and schedule search.
- **Experiment 002** — seeded nucleation and moving frontier.
- **Experiment 003** — damage/recovery controls with cooperative, no-coupling, and brute-force baselines.
- **Experiment 004** — minimal tabular Q-learning on held-out damage.
- **Experiment 005** — preregistered generalization matrix: learned control lowers declared effort in an easy/saturated regime.
- **Experiment 006** — preregistered over-hard negative boundary: no tested controller succeeds.
- **Experiment 007** — preregistered controllability curve: learned and cooperative both reach `lambda50=0.80`; random reaches `0.60`.
- **Experiment 008** — preregistered rich-state ablation: richer geometry/history observation does **not** shift `lambda50`, but lowers median declared effort at the shared boundary.

## Why COSMIC-ORGANICS matters

The sibling COSMIC-ORGANICS project contributes useful **architectural abstractions**: explicit transitions, local coupling, thresholds, path feedback, sparse frontiers, and separately checkable transition traces. MorphoMatter does not treat COSMIC as calibrated material physics.

See [`docs/COSMIC_BRIDGE.md`](docs/COSMIC_BRIDGE.md).

## Current controllability picture

Experiment 007 found a software transition region between an easy/saturated regime and an over-hard regime:

| lambda | coarse learned | cooperative | random |
|---:|---:|---:|---:|
| `0.00` | `76.6%` | `89.1%` | `81.3%` |
| `0.20` | `71.9%` | `76.6%` | `72.5%` |
| `0.40` | `65.6%` | `65.6%` | `63.3%` |
| `0.60` | `59.4%` | `59.4%` | `51.4%` |
| `0.80` | `50.0%` | `51.6%` | `34.0%` |
| `1.00` | `25.0%` | `25.0%` | `13.5%` |

Preregistered `lambda50` values:

- coarse learned: `0.80`;
- cooperative heuristic: `0.80`;
- random: `0.60`;
- brute-force: `NONE`.

Frozen Experiment 007 label: `CONTROLLABILITY_BOUNDARY_OVERLAP`.

See [`docs/EXPERIMENT_007_RESULTS.md`](docs/EXPERIMENT_007_RESULTS.md).

## Experiment 008 — richer observation without changing control

Experiment 008 tests a causal hypothesis: perhaps the learned controller stopped at the same boundary as the cooperative heuristic because its observation was too coarse.

The **coarse** state contains:

- ordered fraction;
- metastable fraction;
- active-frontier fraction.

The **rich** state keeps those features and adds:

- largest connected non-ordered component;
- number of non-ordered components;
- mean ordered-neighbor support on the frontier;
- recent ordered-commit progress;
- remaining recovery-horizon bucket.

The transition law, lambda grid, action set, Q-learning reward/hyperparameters, training budget, damage geometries, stochastic seeds, goal, and horizon remain frozen relative to Experiment 007.

Preregistered result:

| Controller | lambda50 |
|---|---:|
| rich learned | `0.80` |
| coarse learned | `0.80` |
| cooperative | `0.80` |
| random | `0.60` |

Frozen label: `RICH_STATE_EFFORT_ONLY`.

At the shared boundary `lambda=0.80`:

| Controller | Success | Median declared effort |
|---|---:|---:|
| rich learned | `32/64` (`50.0%`) | **`1.470`** |
| coarse learned | `32/64` (`50.0%`) | `1.795` |
| cooperative | `33/64` (`51.6%`) | `2.280` |

So richer observation improves **condition-selection efficiency near the boundary**, but does not expand the current reachable region. This points away from observation poverty as the sole cause of the Experiment 007 ceiling and toward constraints in the action space and/or transition surrogate.

Preregistration: [`docs/EXPERIMENT_008_PREREGISTRATION.md`](docs/EXPERIMENT_008_PREREGISTRATION.md).  
Full result: [`docs/EXPERIMENT_008_RESULTS.md`](docs/EXPERIMENT_008_RESULTS.md).

## Verify

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python experiments/nucleation_frontier.py
PYTHONPATH=src python experiments/damage_recovery.py
PYTHONPATH=src python experiments/learned_recovery.py
PYTHONPATH=src python experiments/generalization_matrix.py
PYTHONPATH=src python experiments/hard_transition_regime.py
PYTHONPATH=src python experiments/controllability_boundary.py
PYTHONPATH=src python experiments/rich_state_boundary.py
```

## Non-claims

This repository does not yet establish:

- a physical programmable material;
- nanoscale robots;
- a calibrated phase diagram or real material phase boundary;
- AI superiority over conventional control in physical systems;
- physical self-repair;
- physical energy, speed, or scaling advantages.

All transition laws and effort metrics are dimensionless software constructs. The current experiments support bounded claims about condition-selection algorithms inside this synthetic model only.
