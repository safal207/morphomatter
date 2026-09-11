# Experiment 003 — Damage → Renucleation → Recovery

## Question

After an ordered state is partially destroyed, can a low-drive condition schedule use local coupling to recover order more effectively than a no-coupling control and more efficiently than a high-drive brute-force control?

## Scope

This is a **dimensionless algorithmic comparison**. It is not evidence of physical self-healing, material repair, crystallization kinetics, fracture mechanics, or energy efficiency.

Experiment 003 deliberately keeps damage and recovery separate:

1. build the pinned Experiment 002 reference state;
2. apply an explicit deterministic damage intervention to that state;
3. start a fresh recovery model from the damaged state;
4. compare three recovery strategies on the same state and deterministic stochastic surface.

The one-way nucleation model therefore does not claim to simulate the physical destruction process itself.

## Pinned starting state and damage

The Experiment 002 reference is rebuilt exactly:

- lattice: `9 × 9`;
- assembly seed: `26`;
- reference ordered sites: `77 / 81`;
- damage rectangle: rows `2..5`, columns `2..6` (zero-based);
- damaged sites: `20`;
- ordered sites removed by damage: `20`;
- post-damage ordered sites: `57 / 81` (`0.703704`).

## Recovery controls

All three recovery cases use recovery seed `11` and run for 12 ticks.

### A. Cooperative coupling

- ticks `1..2`: `drive=0.55`, `coupling_scale=1.0`, `threshold_scale=0.8`;
- ticks `3..12`: `drive=0.12`, `coupling_scale=1.5`, `threshold_scale=0.8`.

This is the candidate mechanism: a brief renucleation pulse followed by lower direct drive and stronger neighbor coupling.

### B. No-coupling control

The same two-tick renucleation pulse, then:

- ticks `3..12`: `drive=0.12`, `coupling_scale=0.0`, `threshold_scale=0.8`.

This asks how much recovery remains when the candidate local-coupling mechanism is disabled.

### C. Brute-force high-drive control

- ticks `1..12`: `drive=0.80`, `coupling_scale=0.0`, `threshold_scale=0.8`.

This asks whether simply applying much stronger direct drive can recover the state without the candidate coupling mechanism.

## Declared control-effort metric

The comparison uses the same intentionally simple dimensionless score family as the transition-map explorer:

```text
|drive| + 0.1 |coupling_scale - 1| + 0.1 |threshold_scale - 1|
```

summed over the schedule.

This score is only a declared algorithmic actuation baseline. It is **not physical energy, power, work, cost, or efficiency**.

## Pinned observation

Under the declared seeds, damage, schedules, and current algorithmic model:

| Strategy | Final ordered fraction | First tick ≥ 90% | Control effort | Gain / effort |
|---|---:|---:|---:|---:|
| cooperative coupling | `1.000000` | `5` | `3.040` | `0.097466` |
| no coupling | `0.901235` | `12` | `3.540` | `0.055800` |
| brute-force high drive | `0.987654` | `7` | `11.040` | `0.025720` |

The cooperative trace contains `nucleation`, `frontier_growth`, and `commit` events and replays exactly from the damaged state.

## Acceptance criteria

The pinned run must:

- remove exactly 20 ordered sites from the Experiment 002 reference;
- recover to at least `99%` ordered under cooperative coupling;
- cross `90%` ordered by recovery tick 6 under cooperative coupling;
- outperform the no-coupling control on final ordered fraction;
- outperform brute-force high drive on gain per declared control effort;
- observe renucleation, frontier growth, and commit in the cooperative trace;
- exactly replay every recovery trace.

## Interpretation boundary

A passing result supports only this bounded statement:

> In the current seeded toy model, the declared low-drive + local-coupling recovery schedule restores a fixed damaged state faster than the no-coupling control and with higher gain per declared control effort than the high-drive control.

It does **not** establish physical self-repair. The scientific next step is to choose a real material platform and replace dimensionless probabilities and control effort with measured physical variables and outcomes.
