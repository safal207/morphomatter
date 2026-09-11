# Experiment 011 — critical transition surface discovery preregistration

## Question

Does the frozen one-way `NucleationLattice` transition law contain distinct, reproducible zero-crossing surfaces in global condition space that play the role of software analogues of phase-transition boundaries?

This experiment characterizes the existing synthetic law. It does not add a new material model and does not claim a physical phase diagram.

## Frozen model

Use the same `EASY_CONFIG` and `HARD_CONFIG` interpolation used in Experiments 007–010, at:

`lambda = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)`.

The transition law itself is not modified.

## Frozen condition grid

Threshold scales:

`(0.70, 0.75, 0.80, 0.85, 0.90)`.

Control envelope remains the Experiment 009/010 envelope:

- `drive ∈ [0.02, 0.80]`;
- `coupling_scale ∈ [0.00, 1.80]`;
- `threshold_scale ∈ [0.70, 0.90]`.

Numerical scan resolution:

- drive step: `0.01`;
- coupling step: `0.01`.

## Frozen critical surfaces

### C1 — nucleation onset

For a `DISORDERED` site with zero ordered-neighbor support, define the nucleation surface as the zero crossing of the unclamped transition propensity:

`spontaneous_rate + nucleation_drive_gain * drive - barrier * threshold_scale = 0`.

For every `(lambda, threshold_scale)`, record the critical drive and classify it as:

- `BELOW_ENVELOPE`;
- `IN_ENVELOPE`;
- `ABOVE_ENVELOPE`.

### C2 — frontier onset

Use one ordered neighbor in an interior von Neumann neighborhood, so frozen ordered-neighbor fraction is:

`q = 0.25`.

Freeze propagation drive at:

`drive = 0.12`.

Define the frontier surface as the zero crossing of:

`frontier_base + frontier_neighbor_gain * q * coupling_scale + frontier_drive_gain * drive - barrier * threshold_scale = 0`.

Record the critical coupling and envelope classification for every `(lambda, threshold_scale)`.

### C3 — commit onset

Using the same `q = 0.25` and `drive = 0.12`, define the `METASTABLE → ORDERED` commit surface as the zero crossing of:

`commit_base + commit_neighbor_gain * q * coupling_scale + commit_drive_gain * drive - barrier * threshold_scale = 0`.

Record its critical coupling and envelope classification.

## Numerical discovery check

For C1, scan drive from `0.02` to `0.80` in steps of `0.01` and record the first grid point with positive transition propensity.

For C2 and C3, scan coupling from `0.00` to `1.80` in steps of `0.01` and record the first grid point with positive transition propensity.

If the analytic critical point is inside the control envelope, the scan-discovered boundary must agree within one grid step plus floating-point tolerance (`<= 0.010000001`).

If the analytic point is outside the envelope, the scanner must correctly report no in-envelope crossing or the appropriate boundary classification.

## Primary report

Report full 6 × 5 surface maps and highlight the reference slice at `threshold_scale = 0.80`.

The primary result label is:

- `TRANSITION_SURFACES_RESOLVED` if all 90 analytic surface points (3 mechanisms × 6 lambdas × 5 threshold scales) classify consistently and every in-envelope numerical scan agrees with the analytic zero crossing within the frozen tolerance;
- `SURFACE_MODEL_INCONSISTENT` otherwise.

## Directionality limitation

The current model is one-way:

`DISORDERED → METASTABLE → ORDERED`.

Therefore Experiment 011 does **not** define or infer a reverse melting/disordering surface. `reverse_surface = UNDEFINED_ONE_WAY_MODEL` must be reported explicitly.

A reversible/hysteretic phase model, if pursued, must be a new experiment and must not be retrofitted into Experiment 011 after seeing results.

## Non-claims

Experiment 011 does not establish:

- physical freezing or boiling points;
- a calibrated material phase diagram;
- real thermodynamic criticality;
- physical temperature, pressure, field, or energy units;
- physical hysteresis or reversibility.

The intended claim is narrower: locate zero-crossing transition surfaces of the frozen synthetic MorphoMatter law and verify that a numerical condition scan recovers them.