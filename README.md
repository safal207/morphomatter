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

The reference acceptance boundary is at least `90%` ordered sites by tick 24 under the pinned dimensionless seed/configuration. This is an algorithmic observation, **not a physical crystallization result**.

See [`docs/EXPERIMENT_002_NUCLEATION.md`](docs/EXPERIMENT_002_NUCLEATION.md).

## Verify

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Non-claims

This repository does not yet establish:

- a physical programmable material;
- nanoscale robots;
- a calibrated phase diagram;
- AI superiority over conventional control;
- self-repair in a physical system;
- physical energy, speed, or scaling advantages.

The current explorer's control cost is a declared algorithmic baseline, **not physical energy**. The next scientific milestone is calibration against a declared physical experiment and comparison of learned control against strong conventional baselines.
