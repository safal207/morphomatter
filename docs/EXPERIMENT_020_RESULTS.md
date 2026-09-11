# Experiment 020 — Translational self-assembly with directional particles — results

## Provenance

Preregistration before any Experiment 020 scientific result:

`e44025d3da50a8626148fe8908b372353490e277`

First completed scientific implementation / CI head:

`2346935c6d2a60823a28d989fa98cb845f5e3f91`

First completed exact-head GitHub Actions run:

`34647887075` — **SUCCESS**.

Job:

`103422920051`.

The run passed `91` unit tests and Experiments `002–020`.

Experiment 020 evaluated `128` preregistered translational + rotational anneal trajectories:

`4 particle topologies × 32 seeds`.

All replay and background controls passed:

- `replay_failures = 0`;
- `control_failures = 0`.

## Frozen result

`TRANSLATIONAL_DYNAMICS_PRESERVE_DIRECTIONAL_SELECTION`

Contact topology was not declared in advance. Particles occupied distinct sites on a periodic `6×6` lattice, translated between unoccupied nearest-neighbor sites, rotated by quarter turns, and formed active bonds only when their current spatial adjacency and facing Experiment 018 directional ports produced positive bond strength.

## Final median structural summary

| particle | beta0 utilization | final utilization | delta utilization | largest component | mean active degree | axial fraction | corner fraction | branch fraction | cross fraction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `isotropic4` | `0.218750` | `0.562500` | `0.375000` | **`1.000000`** | **`2.250000`** | `0.000000` | `0.375000` | `0.375000` | `0.000000` |
| `axial2` | `0.125000` | `0.750000` | `0.625000` | `0.625000` | `1.500000` | **`0.500000`** | `0.000000` | `0.000000` | `0.000000` |
| `corner2` | `0.062500` | **`0.875000`** | **`0.875000`** | `0.500000` | `1.750000` | `0.000000` | **`0.750000`** | `0.000000` | `0.000000` |
| `tri3` | `0.166667` | `0.666667` | `0.583333` | **`1.000000`** | `2.000000` | `0.125000` | `0.375000` | **`0.250000`** | `0.000000` |

## Preregistered topology signatures

All four topology-specific structural signatures passed:

- `isotropic4`: higher coordination than `axial2` and `corner2`;
- `axial2`: straight/opposite degree-2 contacts dominate over corner contacts;
- `corner2`: orthogonal/corner degree-2 contacts dominate over straight contacts;
- `tri3`: branching exceeds both `axial2` and `corner2` by the preregistered margin.

Frozen summary:

`signature_map={'isotropic4': True, 'axial2': True, 'corner2': True, 'tri3': True}`

`signature_passes=4/4`.

## Assembly gain

All four topologies increased median binding utilization relative to the post-beta0 reference:

- `isotropic4`: `+0.375000`;
- `axial2`: `+0.625000`;
- `corner2`: `+0.875000`;
- `tri3`: `+0.583333`.

Frozen summary:

`assembly_passes=4/4`.

## Connectivity

All four topologies met the preregistered median largest-component criterion `>= 0.50`:

- `isotropic4 = 1.000`;
- `axial2 = 0.625`;
- `corner2 = 0.500`;
- `tri3 = 1.000`.

Frozen summary:

`connectivity_passes=4/4`.

## Anneal trajectory evidence

Median binding utilization increased with the anneal schedule for all four particle families.

### isotropic4

`0.21875 -> 0.25 -> 0.25 -> 0.34375 -> 0.46875 -> 0.5625`

Median largest-component fraction reached `1.0` at beta `8`.

### axial2

`0.125 -> 0.125 -> 0.25 -> 0.375 -> 0.625 -> 0.75`

The final median axial signature was `0.50` with corner signature `0.0`.

### corner2

`0.0625 -> 0.125 -> 0.25 -> 0.375 -> 0.75 -> 0.875`

The final median corner signature was `0.75` with axial signature `0.0`.

### tri3

`0.166667 -> 0.208333 -> 0.25 -> 0.333333 -> 0.583333 -> 0.666667`

Median largest-component fraction reached `1.0`, with final branch fraction `0.25`.

## Strongest supported claim

Within this declared synthetic lattice Monte Carlo surrogate:

`directional particle topology -> emergent local contact geometry -> distinct assembled structural signature`

remains observable after explicit particle translation is introduced and the contact graph is no longer predeclared.

This is stronger than Experiments 018–019 in one specific architectural sense: the particles now have to create and destroy contacts by moving on the lattice rather than optimizing orientations on a frozen contact network.

The result supports a software-level design principle:

**equal scalar interaction budget does not imply equal emergent structure; the directional organization of that budget can shape the self-assembled attractor.**

## Frozen background controls

The Experiment 016/017 background condition remained:

`q_rel=1.0, I=1.0 -> REVERSIBLE_ASSEMBLY`.

The Experiment 015 hard-interface control remained:

`IC-C1(theta=180°, lambda=1.00) = 0.700000000`.

Directional particle budgets remained exactly `2.0`.

## Important limitations

- The lattice is only `6×6` with 8 particles.
- Translation is discrete nearest-neighbor motion, not Brownian dynamics.
- The Metropolis-like beta coordinate is dimensionless and not a calibrated physical temperature.
- There is no hydrodynamics, inertia, solvent transport, long-range force field, continuous particle position, rotational diffusion, particle collision geometry, or calibrated chemistry.
- The Experiment 016 environment is used as a declared background control; its continuous interaction potential is not yet directly coupled to the Exp020 move energy.
- The topology signatures were preregistered from the directional-port architecture and therefore validate causal selectivity in this surrogate; they do not predict a real material morphology.

## Next causal layer

The clean next experiment is to couple the Experiment 016/017 `particle property × environment` interaction window directly into the Exp020 translational dynamics.

A strong Experiment 021 should hold the directional particle topology fixed and drive the environment coordinate `I` across `DISPERSED_BARRIER -> REVERSIBLE_ASSEMBLY -> KINETIC_TRAP_RISK`, then test whether spatial assembly/disassembly trajectories follow the predicted window and whether forward/reverse environment sweeps create path dependence.

That would connect:

`object property × environment property -> interaction landscape -> actual motion/contact creation -> structure trajectory`.

## Non-claims

Experiment 020 does not establish:

- physical programmable matter;
- real colloidal yield or material morphology;
- physical Brownian motion or temperature;
- calibrated bond energies;
- a laboratory particle recipe;
- a real phase transition;
- anomalous fields, pyramid effects, water-memory effects, or physical energy savings.
