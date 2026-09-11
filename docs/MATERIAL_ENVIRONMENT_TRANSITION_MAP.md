# MorphoMatter — Material × Environment × Interface × Transition map

## Central research object

MorphoMatter should not treat geometry, temperature, field strength, or any other single variable as the cause of a transition by itself.

The primary object is the coupled system:

`object/material properties × environment properties × interface properties × interaction law × trajectory/history -> transition probability -> evolving structure`

A useful software abstraction is:

`P(S_{t+1} | S_t, M, E, I, X, H_t)`

where:

- `M` = material/object properties;
- `E` = environment properties;
- `I` = interface/boundary properties;
- `X` = interactions and external fields;
- `H_t` = path/history;
- `S_t` = current micro/macro state.

This document is a research map, not a calibrated physical model.

## 1. Material / object properties

### Composition and phase identity

- chemical composition / species fractions;
- crystal or amorphous phase;
- alloy / polymer / colloid / gel / granular class;
- solvent or carrier compatibility;
- impurities / dopants / additives.

### Particle / building-block geometry

- size distribution;
- aspect ratio;
- shape anisotropy;
- surface area to volume ratio;
- roughness / faceting;
- porosity.

### Mechanical properties

- elastic modulus;
- yield / plastic response;
- fracture / adhesion strength;
- particle stiffness / softness;
- compressibility;
- internal stress / residual stress.

### Electrical / magnetic / optical properties

- charge / zeta-potential proxy;
- dielectric response;
- conductivity;
- polarizability;
- magnetic susceptibility / moment;
- optical absorption / photo-response.

### Thermal / transport properties

- thermal conductivity;
- heat capacity;
- diffusivity;
- species mobility;
- permeability.

## 2. Environment properties

### Thermodynamic coordinates

- temperature;
- pressure;
- chemical potential;
- concentration / supersaturation;
- humidity / solvent activity.

### Chemical environment

- pH;
- ionic strength;
- salt / counter-ion identity;
- redox potential;
- solvent polarity;
- reactive species concentrations;
- catalytic / inhibitory species.

### Rheology / transport

- viscosity;
- diffusion coefficients;
- flow velocity / shear rate;
- convection;
- boundary-layer thickness;
- reaction–diffusion time scales.

### External fields

- electric field;
- magnetic field;
- acoustic field;
- optical illumination;
- mechanical load / vibration;
- thermal gradient;
- concentration / chemical gradients.

## 3. Interface and boundary properties

Interfaces are first-class state variables because phase transformations and self-assembly often depend on interfacial energetics and kinetics rather than only bulk values.

Track at least:

- interfacial / surface energy;
- wettability / contact-angle proxy;
- adhesion;
- surface charge / chemistry;
- roughness / curvature;
- heterogeneous nucleation-site density;
- pore / confinement dimensions;
- wall permeability / no-flux / fixed-value / fixed-flux boundary type;
- source / sink geometry;
- interface elasticity / stress.

## 4. Interaction laws

A future MorphoMatter physical surrogate should permit multiple interaction channels rather than one generic `coupling_scale`.

Candidate channels:

- attraction / repulsion;
- electrostatic / screened electrostatic;
- van der Waals;
- steric / polymer brush;
- magnetic dipole;
- capillary;
- depletion;
- hydrogen bonding / ligand binding;
- covalent / coordination reactions;
- friction / contact mechanics;
- hydrodynamic coupling;
- catalytic / reaction-network coupling.

The controller should not be told that one channel is always helpful. It should discover when changing environment variables changes the effective interaction landscape.

## 5. Transition properties

A transition is not only an endpoint threshold.

For every candidate transition track:

- forward critical surface;
- reverse critical surface;
- nucleation barrier;
- growth/front velocity;
- coarsening / defect-annihilation rate;
- metastable lifetime;
- hysteresis width;
- reversibility;
- stochastic success probability;
- spatial initiation sites;
- structural defects after transition;
- history dependence.

Useful decomposition:

`transition = nucleation + propagation + relaxation/coarsening`

and, for reversible systems:

`A -> B` and `B -> A` should have separately measured surfaces.

## 6. History / trajectory

The same instantaneous state variables can produce different outcomes depending on path.

Track:

- ramp rate;
- dwell time;
- sequence of fields / chemical changes;
- prior phase;
- number of prior cycles;
- damage / defects;
- aging;
- previous nucleation sites.

Therefore the more complete model is:

`Structure_t = f(M, E(t), I(t), X(t), trajectory[0:t], stochastic history)`.

## 7. Causal graph for experiments

A useful default causal graph is:

`material properties`
`      +`
`environment properties`
`      +`
`boundary/interface properties`
`      v`
`local transport fields`
`      v`
`effective interaction strengths`
`      v`
`local transition propensity`
`      v`
`nucleation`
`      v`
`front propagation / growth`
`      v`
`microstructure`
`      v`
`macroscopic function`

Experiments should intervene on one layer at a time whenever possible.

## 8. Measurement / evidence schema

Each experimental transition record should eventually contain:

- material-property manifest;
- environment-property manifest;
- boundary/interface manifest;
- initial microstructure descriptor;
- applied trajectory;
- observed local fields;
- transition events;
- final structure descriptor;
- functional-property measurement;
- random seed / calibration data where appropriate;
- hashes / provenance;
- explicit non-claims.

## 9. Recommended progression beyond Experiment 014

Experiment 014 isolates equal-total-flux geometry.

Then move from one-factor geometry studies toward a factorial/causal hierarchy:

1. **015 — Interface chemistry / wettability surrogate**: same geometry and transport, vary declared heterogeneous nucleation affinity only.
2. **016 — Environment chemistry surrogate**: concentration / pH / ionic-strength-like coordinates alter interaction channels, not geometry.
3. **017 — Particle-property matrix**: size/shape/charge/interaction-anisotropy descriptors alter local interaction law.
4. **018 — Reversible phase-field surrogate**: explicit free-energy landscape, forward/reverse transition and hysteresis.
5. **019 — Coupled reaction–diffusion + phase transition**: environment is produced and consumed dynamically rather than supplied as a static field.
6. **020 — Multi-property controller**: AI searches trajectories across environmental coordinates while material properties remain fixed and held-out combinations test generalization.

## 10. Scientific boundary

MorphoMatter software can test causal architecture and controller logic, but physical claims require calibrated parameters and experiments.

Do not translate a dimensionless threshold directly into a real temperature, pH, field, pressure, concentration, or material property without an explicit physical mapping and validation dataset.

The central hypothesis to test is narrower and stronger:

> Desired self-organization can sometimes be produced more effectively by controlling the coupled material–environment–interface transition landscape than by commanding individual building blocks.
