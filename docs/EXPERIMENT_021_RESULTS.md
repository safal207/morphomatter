# Experiment 021 — Environment-coupled contact-energy cycle: results

## Status

The previously incomplete adapter in PR #12 now has regression tests, a runnable experiment, and a completed dedicated GitHub Actions validation run. Experiments 018–020 already existed and were not duplicated.

Frozen prospective protocol and original material/dynamics adapter were not changed. This result is a finite synthetic lattice Monte Carlo result, not physical programmable matter and not an AI-learning result.

## Provenance

- Preregistration: `af50186071ff320fe2b799e031359ddeb90bf29a`.
- Original adapter: `3550d8c4c7ff32f1639ce536cd83dccef802b067`.
- Added integrity tests: `eb64bedd9f0edb58e96a5954bc4bb1aeffb2d6a6`.
- Added runner: `1e3a3f3fb3d4f9a9449fee3c3a7574d7621b05b5`.
- Implementation/validation head: `08ad97e452a2659980adb28686a0586b45ecb858`.
- Dedicated PR workflow run: `34689379971`, job `103541848500`, **SUCCESS**.
- Actual checked-out PR merge ref: `3a577af137b3cdc1106dcc2e8e7ffe0b3d76cf1f`, combining the implementation head with parent `bf969b6e87d9eaafb012c4e2bab405b52e6f33ea`.
- Observed run: 2026-09-12, 10:47–10:48 UTC.

The dedicated job passed all **18 new integrity tests** and executed the complete Exp021 protocol. The separate historical regression workflow `34689379956` was still running when this document was written; its unit-test step had passed. This document does not label that entire historical run as complete.

## Frozen result

`ENVIRONMENT_COUPLED_ASSEMBLY_AND_RELEASE`

All prospective primary criteria passed. The secondary finite-rate path-separation flag did **not** pass at either rate.

## What was actually simulated

One frozen topology (`axial2`), eight particles, a periodic 6×6 lattice, and dimensionless beta=8. Particles translate and rotate through symmetric local proposals with excluded occupancy.

The external environment follows:

`0.01 -> 0.03 -> 0.10 -> 0.30 -> 1 -> 3 -> 10 -> 3 -> 1 -> 0.30 -> 0.10 -> 0.03 -> 0.01`.

The Hamiltonian is the preregistered contact-only projection:

`H = U_rep(0,I) * occupied_neighbor_contacts - total_directional_bond_strength`.

Repulsion includes directionally incompatible occupied contacts. Static classifier labels do not select moves. The environment changes Metropolis acceptance through the energy difference.

There were 16 seeds at each of two rates, **32 primary trajectories**, **32 exact repeats**, and **4 pairs of fixed-energy label counterfactuals**. These are stochastic replicates of one small model, not 32 different materials.

## Primary endpoints

Binding utilization is total directional bond strength divided by 8. It is not the fraction of particles in a crystal, a success probability, or a measured material property.

| Sweeps per stage | Median initial utilization | Median high-I utilization | Mean high-I utilization | High-I range | Median relaxed utilization |
|---:|---:|---:|---:|---:|---:|
| 32 | 0 | 0.625 | 0.6640625 | [0.500, 0.875] | 0 |
| 256 | 0 | 0.750 | 0.7421875 | [0.625, 0.875] | 0 |

At the preregistered primary slow rate (256 sweeps per stage):

- median assembly gain = **0.750**, criterion >=0.25;
- median release drop = **0.750**, criterion >=0.25;
- median return error = **0.000**, criterion <=0.125;
- median relaxed utilization = **0.000**, criterion <=0.125.

Mean assembly gain and mean release drop were both **0.7421875**. Their separately seeded 95% percentile bootstrap intervals for the mean were both **[0.7109375, 0.7734375]**, using 2000 resamples and the preregistered RNG seeds 21101 and 21102.

Every primary trajectory had zero directional utilization and zero occupied nearest-neighbor contacts after final low-I relaxation. This is return to an unbound state under the declared metric, not recovery of the original particle positions/orientations.

## Secondary endpoint: no threshold-level path-memory signal

Normalized absolute outward/return separation over log10(I):

| Sweeps per stage | Area | Descriptive threshold | Flag |
|---:|---:|---:|---|
| 32 | 0.0182291667 | >=0.05 | false |
| 256 | 0.0130208333 | >=0.05 | false |

The curves are not exactly identical, but neither area reaches the frozen threshold. No equilibrium hysteresis, permanent memory, or confidence-qualified rate effect is established.

Slow-rate means:

| I-like | Outward utilization | Return utilization | Return minus outward |
|---:|---:|---:|---:|
| 0.01 | 0 | 0 | 0 |
| 0.03 | 0 | 0 | 0 |
| 0.10 | 0 | 0 | 0 |
| 0.30 | 0.0234375 | 0.015625 | -0.0078125 |
| 1.00 | 0.421875 | 0.4296875 | +0.0078125 |
| 3.00 | 0.671875 | 0.734375 | +0.0625000 |
| 10.00 | 0.7421875 | 0.7421875 | 0 |

## Counterfactual and implementation checks

- replay failures = **0**;
- external-label counterfactual failures = **0**;
- recorded trace-invariant failures = **0**;
- independent pair-energy oracle agrees with local/global changes across sampled states and all four existing port topologies;
- Metropolis acceptance-ratio tests pass for symmetric proposals;
- blocked proposals consume the acceptance draw;
- invalid/nonfinite environment values and invalid sweep counts are rejected.

For the fixed-energy controls, replacing the whole varying external-label schedule with constant labels produced exactly the same mechanical traces. The control's own high-minus-low utilization was not required to be zero: its median was 0.25 over four seeds, reflecting finite-time evolution at constant energy parameters. It must not be described as a zero-drift baseline.

A separate local read-only audit of the downloaded evidence recomputed contacts, directional utilization, and Hamiltonians directly from all **448 primary recorded snapshots**, using unordered particle pairs rather than the production neighborhood functions. It found **0 discrepancies**, verified the four counterfactual trace pairs, and matched both archive and trace hashes. This is a second implementation check by the same assistant, not independent external replication.

## Evidence artifacts

GitHub run: https://github.com/safal207/morphomatter/actions/runs/34689379971

Artifact ID: `10296876595`, containing:

- `experiment_021_summary.json` — criteria, statistics, provenance and source SHA-256 values;
- `experiment_021_traces.json` — full stage states for primary and counterfactual runs;
- `experiment_021_stages.csv` — 448 primary stage/relaxation records.

Archive SHA-256:

`526e453ea9fe1a1dd4c98dce7bb92b464517d9d802e3b7cef145519561980904`

Canonical compact traces SHA-256 (excluding terminal newline):

`bfc0c199c4355d7d1ebecbaf15a8c5d86462f6c04dff28c62d5124487e1a30a1`

Artifacts have a declared 30-day retention. The runner regenerates the files; preserve a copy for longer-term use.

## Strongest supported conclusion and limits

Within this declared contact-only model, changing an actual energy input causes contact assembly and low-I release under a frozen environment trajectory; merely relabeling the environment cannot do so. This goes beyond a static interaction-regime classification.

However, Exp016/017 static `I_access` and `I_trap` roots are NOT validated by this experiment. This Hamiltonian samples their potential only at h=0, omitting its radial barrier. The old label `KINETIC_TRAP_RISK` at I=10 is not a measured irreversible trap here: these runs release when low-I conditions are restored.

No physical salt concentration, Debye length, pH, Kelvin temperature, real material recipe, thermodynamic phase boundary, laboratory reversibility, learned AI controller, or physical energy savings are established. Thresholds, port topology, and coarse-graining are explicit model assumptions; a passing CI verifies computation, not those assumptions against nature.
