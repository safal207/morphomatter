# COSMIC → MorphoMatter bridge

MorphoMatter does **not** treat COSMIC-ORGANICS as a physical model. The transfer is architectural: useful abstractions for reasoning about self-organization are re-expressed as dimensionless hypotheses that can later be calibrated against real material data.

## Reused abstractions

1. **Transition-state execution** — model state changes as explicit boundary crossings rather than direct placement commands.
2. **Conditions, thresholds, coupling** — a site changes because external drive plus neighbor influence crosses a threshold.
3. **Path feedback** — if a trajectory stops improving, change the conditions rather than moving individual particles.
4. **Hierarchical coupling** — local domains may organize strongly before global structure aligns.
5. **Active frontier** — future optimization should update only regions whose conditions or neighborhood changed, after equivalence is proven against a dense reference.
6. **Transition trace + replay** — the controller must not be allowed to rewrite evidence; completed transitions are recorded and replayable.
7. **Nucleation/frontier hypothesis** — MorphoMatter Experiment 002 adds seeded rare local transitions followed by neighbor-assisted propagation. This is a new MorphoMatter toy mechanism, not a physical claim inherited from COSMIC.

## MorphoMatter translation

```text
COSMIC abstraction        MorphoMatter hypothesis
----------------------    -------------------------------------------
stimulus                  controllable environment / field schedule
phase A/M/C               disordered / metastable / ordered state
neighbor coupling         local interaction strength
threshold                 phase-transition boundary
memory                     path/history dependence
path gradient              condition adjustment when progress stalls
transition trace           experimental provenance / replay record
active frontier            moving region of material change
```

## Critical boundary

The current v0 model is **dimensionless and algorithmic**. `drive`, `coupling_scale`, and `threshold_scale` are not temperature, pressure, magnetic field, viscosity, pH, or any other calibrated material quantity.

Experiment 002 also introduces dimensionless nucleation/frontier probabilities. Their names describe the algorithmic mechanism only; they are not fitted nucleation rates, free-energy barriers, or kinetic constants.

The scientific next step is therefore not to claim smart matter. It is to define a measurable physical system and learn a mapping:

```text
physical conditions x(t) -> observed state S(t) -> transition probability P(S(t+1)|S(t), x(t))
```

Only after experimental calibration may these abstract controls acquire physical units.
