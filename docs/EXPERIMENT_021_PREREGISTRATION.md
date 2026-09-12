# Experiment 021 — Environment-coupled contact-energy cycle

## Status and provenance

Prospective protocol, committed before running Experiment 021. Parent scientific lineage: Experiment 020, branch `exp/translational-assembly-v0`, pinned parent `bf969b6e87d9eaafb012c4e2bab405b52e6f33ea`.

No result label or measured trajectory is asserted here. Negative results must be retained. Do not modify this protocol after viewing results; any repair or extension must be documented separately.

## Question

Does changing the environment coordinate actually change translational/rotational dynamics when an explicit contact-energy projection of the Experiment 016 potential is connected to Experiment 020 particles? Does returning the environment to its initial value disperse the contacts again on a declared observation horizon?

Experiments 016–017 classify a static pair potential with hand-declared thresholds. Their `REVERSIBLE_ASSEMBLY` and `KINETIC_TRAP_RISK` labels do NOT establish kinetic reversibility, crystallization, or trapping. Experiment 020 only checks those modules as background controls; its move energy is independent of I. This experiment connects an energy channel rather than checking an unrelated constant again.

## Frozen model and scope

- Periodic 6 by 6 lattice, 8 excluded-volume particles, four quarter-turn orientations, as in Experiment 020.
- One topology only: frozen `axial2 = (1, 0, 1, 0)`, directional budget 2.
- `q_rel = 1.0`; no treatment of charge, topology, particle number, concentration, or geometry.
- Dimensionless inverse-temperature parameter beta = 8.0 throughout. This is NOT a calibrated Kelvin temperature.
- Nearest-neighbor contacts only; each undirected contact counted once.
- Reuse Experiment 016 functions at surface separation h=0:
  `r(I) = q_rel**2 * repulsive_potential(0, I)`;
  `a = attractive_potential(0) = -1`.
- Reuse Experiment 018 reciprocal-port `bond_strength`, as in Experiment 020.
- Hamiltonian:
  `H(state, I) = r(I) * number_of_occupied_neighbor_contacts + a * sum(directional_bond_strength)`.
- Repulsion applies to ALL occupied neighbor contacts, including contacts with zero directional affinity. Attraction applies only through reciprocal directional affinity.
- There is no state classification, target shape, motif, imposed bond, or regime label in the motion kernel.

This is an explicitly NEW contact-only coarse-graining assumption. It samples the old potential at h=0; it is NOT the full distance-dependent potential, a barrier-crossing model, a solvent simulation, or a calibrated DLVO model. The old I_access/I_trap values are not predictions for this Hamiltonian. In particular, no agreement with those static windows is required for a positive result.

## Frozen proposals and acceptance

Choose one particle uniformly. Choose translation or rotation with probability 1/2. For translation, select one cardinal neighbor uniformly; reject occupied targets. For rotation, choose +1 or -1 quarter turn with equal probability. Draw one acceptance uniform on EVERY proposal, including blocked ones, so proposal randomness remains comparable across interventions.

For valid proposals accept with `min(1, exp(-beta * (H_new-H_old)))`. The proposal is symmetric. Local energy-difference optimization is allowed only with tests against independent whole-state energy differences. At a fixed I the acceptance-ratio check must satisfy detailed balance for this declared Hamiltonian. The driven cycle is not claimed to be at equilibrium.

## Frozen environment cycle and sampling

- Upward I grid: `(0.01, 0.03, 0.10, 0.30, 1.00, 3.00, 10.00)`.
- Full cycle: upward grid followed by its reverse excluding the repeated high endpoint (13 stages).
- Seeds: integers 21001 through 21016 inclusive.
- Initialization: Experiment 020 `random_state(random.Random(seed))`.
- Warmup: 256 sweeps at I=0.01, beta=8.
- Two rates: 32 and 256 sweeps per environment stage.
- One sweep = 8 proposals, including rejected proposals.
- Final relaxation: 512 additional sweeps at I=0.01, beta=8.
- Primary trajectories: 16 seeds times 2 rates = 32; exact repeat of each for reproducibility.
- Record full state, occupied-contact count, Hamiltonian, Experiment 020 spatial metrics, proposal count, and accepted count after each stage and after final relaxation.
- No physical time unit is assigned to a sweep.

## Required counterfactual control

For seeds 21001 through 21004 and the slow rate (256), run the same cycle but freeze the energy environment to I=1.0 regardless of the external I label (`coupled=False`). Repeat using a constant external label sequence of 13 copies of I=1.0, with the SAME seed and fixed-energy mode.

The two runs must have exactly equal mechanical traces: positions, orientations, energies, spatial metrics, contact counts, and proposal/acceptance counts. External labels are intentionally excluded from this equality. Any difference is an implementation failure. Report the control high-minus-low utilization as descriptive information, not an expected exact zero from finite sampling.

## Primary endpoints and decision rule

Use the slow rate and calculate, per seed:

1. `assembly_gain = utilization_at_I10 - utilization_at_first_I0.01`.
2. `release_drop = utilization_at_I10 - utilization_after_final_relaxation`.
3. `return_error = abs(utilization_after_final_relaxation - utilization_at_first_I0.01)`.

Report means, medians and ranges; for paired assembly_gain and release_drop also report percentile bootstrap intervals for the mean (2000 resamples, RNG seeds 21101 and 21102). Seeds are stochastic replicates of this one finite model, not independent material systems.

Return `ENVIRONMENT_COUPLED_ASSEMBLY_AND_RELEASE` only if:

- median assembly_gain >= 0.25;
- median release_drop >= 0.25;
- median return_error <= 0.125;
- median relaxed utilization <= 0.125;
- replay_failures = 0 and counterfactual_control_failures = 0;
- finite-input, detailed-balance and local/global energy tests pass.

Otherwise retain `ENVIRONMENT_CYCLE_MIXED_OR_NEGATIVE`. CI must distinguish a valid negative scientific result from broken invariants: negativity alone does not cause a nonzero exit status.

## Secondary path-dependence endpoint

For each rate, at each shared I compare mean return-leg utilization to mean outward-leg utilization. The high turnaround point is shared. Report the normalized trapezoidal integral of the absolute difference over log10(I), divided by the total log span. Also report all signed per-I differences.

An area >= 0.05 is a descriptive finite-rate path-separation flag only, not a confidence-qualified discovery, equilibrium hysteresis, a phase transition or permanent material memory. No required rate ordering and no positive-result requirement on this secondary endpoint.

## Scope and non-claims

This experiment contains no learned controller. It isolates an environment-to-motion causal channel before adding AI. It cannot establish real chemistry, assembly temperature, salt concentration, particle recipe, physical self-repair, long-range force barriers, or macroscopic controllability. A return of a scalar utilization metric is not a return of every microscopic configuration.

Equal directional budget is not equality of all bond energies, angular bonding volume or kinetics. Only one topology is tested here.

## Primary references (motivation, not calibration)

- Metropolis et al., Equation of State Calculations by Fast Computing Machines, J. Chem. Phys. 21, 1087–1092 (1953), DOI: 10.1063/1.1699114. Symmetric-proposal Monte Carlo basis.
- Chen, Bae and Granick, Directed self-assembly of a colloidal kagome lattice, Nature 469, 381–384 (2011), DOI: 10.1038/nature09713. Experimental motivation for combining directional surface attraction and electrostatic repulsion; its measurements are not reproduced or fitted here.
