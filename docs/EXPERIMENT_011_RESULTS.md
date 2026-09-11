# Experiment 011 — critical transition surface discovery results

## Provenance

Preregistration was committed before the first Experiment 011 result:

`8e5689fd80df92c26542253de1d2a83bf0ebf360`

First completed implementation head:

`34250cc69b0f237babb623b0785d3261d50b62ab`

GitHub Actions PR run:

`34575861017`

The run passed `38` unit tests and Experiments 002–011. Experiment 011 evaluated `90` preregistered surface points and reported `0` inconsistent points.

## Frozen result

Preregistered label:

`TRANSITION_SURFACES_RESOLVED`

The numerical scan recovered the analytic zero-crossing surfaces of the frozen synthetic transition law within the preregistered `0.01` grid tolerance.

`reverse_surface = UNDEFINED_ONE_WAY_MODEL`

The current model remains one-way and therefore does not define a melting/disordering surface.

## Reference slice: threshold_scale = 0.80

| lambda | C1 nucleation critical drive | C1 class | C2 frontier critical coupling | C2 class | C3 commit critical coupling | C3 class |
|---:|---:|---|---:|---|---:|---|
| `0.00` | `0.333333` | `IN_ENVELOPE` | `-0.115200` | `BELOW_ENVELOPE` | `-2.422857` | `BELOW_ENVELOPE` |
| `0.20` | `0.406667` | `IN_ENVELOPE` | `-0.003200` | `BELOW_ENVELOPE` | `-2.094118` | `BELOW_ENVELOPE` |
| `0.40` | `0.480000` | `IN_ENVELOPE` | `0.126031` | `IN_ENVELOPE` | `-1.745455` | `BELOW_ENVELOPE` |
| `0.60` | `0.553333` | `IN_ENVELOPE` | `0.276800` | `IN_ENVELOPE` | `-1.375000` | `BELOW_ENVELOPE` |
| `0.80` | `0.626667` | `IN_ENVELOPE` | `0.454982` | `IN_ENVELOPE` | `-0.980645` | `BELOW_ENVELOPE` |
| `1.00` | `0.700000` | `IN_ENVELOPE` | `0.668800` | `IN_ENVELOPE` | `-0.560000` | `BELOW_ENVELOPE` |

## Full-grid interpretation

The full preregistered map used:

- `lambda = (0.00, 0.20, 0.40, 0.60, 0.80, 1.00)`;
- `threshold_scale = (0.70, 0.75, 0.80, 0.85, 0.90)`;
- nucleation drive scan `0.02 → 0.80` with step `0.01`;
- frontier/commit coupling scan `0.00 → 1.80` with step `0.01`;
- frozen frontier support `q = 0.25`;
- frozen propagation drive `0.12`.

### C1 — nucleation onset

The nucleation critical drive is inside the allowed drive envelope for every one of the 30 `(lambda, threshold_scale)` points.

It moves monotonically upward as either transition difficulty (`lambda`) or threshold scale increases. At the reference threshold `0.80`, it rises from `0.333333` at `lambda=0.00` to `0.700000` at `lambda=1.00`.

This means the frozen software law contains a distinct boundary separating conditions where isolated spontaneous nucleation has zero transition probability from conditions where it becomes possible.

### C2 — frontier onset

The frontier zero crossing changes qualitatively across the map.

At easier regimes it lies below the allowed coupling envelope, meaning an interior site with one ordered neighbor already has positive frontier-growth propensity even at zero coupling under the frozen propagation drive.

As transition difficulty increases, the frontier zero crossing moves into the controllable coupling range. In the reference `threshold_scale=0.80` slice it enters the envelope between `lambda=0.20` and `lambda=0.40`, then rises to `0.668800` at `lambda=1.00`.

Across the full grid, for example, at `lambda=0.20` the frontier root is still below the envelope at thresholds `0.70–0.80`, but enters the envelope at threshold `0.85` (`0.028800`) and `0.90` (`0.060800`).

This provides a second distinct transition surface: once a nucleus exists, sufficient local coupling can itself become a separate condition for propagation.

### C3 — commit onset

Every commit critical-coupling root in the frozen 6 × 5 map lies below the allowed coupling envelope.

At the reference threshold `0.80`, the root rises from `-2.422857` to `-0.560000` as lambda increases, but never reaches zero coupling.

Therefore `METASTABLE → ORDERED` commit is not the onset bottleneck inside the tested control envelope. In the current one-way law, nucleation and frontier growth define the relevant accessible zero-crossing boundaries before commit does.

## Relation to the water analogy

The result supports a software analogue of the user's phase-transition intuition, but not literal `0°C` or `100°C` material points.

Water's familiar phase-change values are slices through a larger phase diagram. Likewise, MorphoMatter's synthetic transition thresholds are not universal scalar constants: they move with the other condition coordinates.

The useful abstraction is:

`critical condition = surface in condition space`,

not a single globally fixed command value.

For the frozen synthetic law, two practically relevant surfaces are now explicit:

1. a nucleation-onset surface;
2. a frontier-propagation onset surface.

The commit surface exists mathematically but lies below the tested coupling envelope and is therefore not the active bottleneck in this map.

## Important limitation: no reverse boundary

Because `NucleationLattice` only permits:

`DISORDERED → METASTABLE → ORDERED`,

Experiment 011 cannot test hysteresis, melting, disordering, or a second reverse phase boundary analogous to cooling/heating loops in physical matter.

A scientifically clean next step is therefore a **new reversible/hysteretic surrogate**, preregistered before results, with forward and reverse transition surfaces kept distinct. That would let us ask whether the same material state depends on the path used to reach it.

## Non-claims

Experiment 011 does not establish:

- physical freezing or boiling points;
- a calibrated material phase diagram;
- real thermodynamic criticality;
- physical temperature, pressure, field, or energy units;
- physical hysteresis or reversibility.

The supported software claim is narrower: **the frozen synthetic MorphoMatter law contains reproducible zero-crossing transition surfaces for nucleation and frontier propagation, and the preregistered numerical scan recovers those surfaces consistently.**