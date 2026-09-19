# Experiment 063 — First executable pilot results

## Status

**Pilot: IMPLEMENTED_AND_EXECUTED. Result: `PILOT_MIXED_OR_NO_GAIN`. Full Experiment 063: NOT_COMPLETED by this increment.**

This report records an actual bounded diagnostic benchmark, not material-dynamics results or external laboratory replication. The [original broad protocol](EXPERIMENT_063_CAUSAL_DISAGREEMENT_RESOLUTION_MARKET.md) remains a roadmap beyond this pilot. Its deferred components are listed explicitly in the [pilot manifest](../experiments/exp063_manifest.json).

## Provenance and execution

| Stage | Immutable reference |
|---|---|
| Pilot scope/parameter freeze, before implementation/results | `c90d4ab65ef8b37d02643d4322bab94c45a8366e` |
| First complete implementation | `4027ee3ec3a0ac159d95e2abdf0757593e8aa94e` |
| Development run | [35452796230](https://github.com/safal207/morphomatter/actions/runs/35452796230), job `105922766360`, SUCCESS |
| Development-selected comparator lock, before held-out evaluation | `7d246f0ef5108922711977d20a3826f42035c6a8` |
| Evaluation run | [35452857186](https://github.com/safal207/morphomatter/actions/runs/35452857186), job `105922928902`, SUCCESS |
| Evaluation checkout | `7d246f0ef5108922711977d20a3826f42035c6a8` |
| Evaluation date | 2026-09-19 |

The implementation-to-evaluation diff adds only `experiments/exp063_comparator_lock.json`. No scientific implementation or test changes were made after observing development results or before held-out evaluation.

Both runs passed **28 unit tests**. Development used 32 worlds (`0..31`); evaluation used 128 different worlds (`1000..1127`). Each world contains 12 binary claim disagreements, 24 unique downstream decisions, and 36 candidate experiments. Six policies share a budget cap of 12 synthetic cost units, the same initial evidence, and the same verifier and claim-decision rule. They need not spend exactly the same amount.

The evaluation contains **768 policy/world records**, each rerun once for exact full-record comparison: **0 replay failures**. This is 128 independent world-level statistical units, not 768 independent worlds and not 18,432 independent decisions.

## What the pilot models

Four independent groups each contain three unknown claim bits and one shared sensor-fault bit. Sensor outcomes depend on the claim and the common fault; a calibration audit measures the fault. Independent replications directly measure a claim. Known aliases refer to the same source; uninformative, failed, inconclusive, and unknown-execution outcomes are also represented.

The scheduler knows this finite likelihood family. It is not discovering arbitrary laws or unknown dependence structures. Its selector does not receive evaluator latent truth or future observations. All policies use the same source/scope verifier and exact finite posterior calculations.

## Comparator selection

The comparator was selected solely by mean realized loss on the 32 development worlds, with a deterministic tie rule. Among non-candidate policies, `information_gain` was best: mean loss `21.5`. The proposed `decision_value` policy had development mean loss `26.15625`.

The comparator and all development metrics were persisted in the [comparator lock](../experiments/exp063_comparator_lock.json) before exposing held-out evaluation outcomes. No switch to a weaker comparator was made after evaluation.

## Held-out results

Each policy makes 3,072 terminal task decisions (128 worlds × 24 tasks). Loss is weighted and synthetic: correct definitive decision = 0, HOLD = 1, wrong definitive decision = 10; task importance weights are 1 or 3. Lower loss is better. HOLD is not a correct resolution, and zero wrong decisions under all-HOLD is not a discovery success.

| Policy | Mean loss/world | Total loss | Correct decisions | Wrong definitive decisions | HOLD | Mean cost spent |
|---|---:|---:|---:|---:|---:|---:|
| Decision value | 17.5625000 | 2248 | 2384 | 56 | 632 | 12.0000000 |
| Information gain (locked comparator) | 20.6484375 | 2643 | 2396 | 77 | 599 | 11.5625000 |
| Importance heuristic | 27.4687500 | 3516 | 1736 | 58 | 1278 | 11.6171875 |
| Random feasible | 29.5156250 | 3778 | 1553 | 43 | 1476 | 12.0000000 |
| Cheapest feasible | 33.0234375 | 4227 | 1322 | 41 | 1709 | 11.6093750 |
| All-HOLD | 47.7343750 | 6110 | 0 | 0 | 3072 | 0.0000000 |

Primary paired difference: `loss_information_gain - loss_decision_value`.

- Mean difference: **3.0859375** synthetic loss units per world.
- 95% paired whole-world percentile bootstrap interval: **[-0.5861328125, 7.0625]**.
- Bootstrap: 10,000 resamples, seed `63059`.
- The interval includes zero, so the preregistered positive-pilot rule is **not met**.
- Observed wrong-definitive count is lower (56 versus 77), but no separate significance claim is made for this secondary comparison.
- The proposed policy also withholds more conclusions (632 versus 599) and uses a slightly larger realized budget.

The point estimate is about 14.95% lower mean loss than the comparator; that percentage is **not an established improvement**. The result is compatible with no advantage under the stated uncertainty estimate. The protocol label remains **`PILOT_MIXED_OR_NO_GAIN`**.

## Correctness versus scientific performance

Across all evaluated policies:

- budget violations: **0**;
- known-invalid evidence-use detections: **0**;
- invalid ledger chains: **0**;
- replay failures: **0**.

These software checks do **not** imply zero wrong scientific decisions. The table explicitly reports nonzero wrong decisions. Unknown common bugs, model misspecification, or hidden dependence are not ruled out by the zero-leakage result.

Unit tests additionally verify duplicate-source invariance, source/scope binding, same-source conflict quarantine, removal of stale evidence while preserving independent sources, positive-cost checks, failed/unknown receipt accounting, no repeated source dispatch, and content-bound comparator-lock rejection.

One analytical unit fixture deliberately demonstrates a limitation: a sensor measuring `claim XOR fault` and a separate fault audit each have zero immediate decision value under the symmetric prior, but together reveal the claim. The greedy value policy stops. This is a validated tiny counterexample to greedy optimality, **not proof that it explains the aggregate held-out result**. Large-scale two-step policy comparison is still deferred.

## Computational overhead

Observed policy execution time on this one CI runner for all 128 worlds, excluding replay:

| Policy | Seconds |
|---|---:|
| Decision value | 5.811198296 |
| Information gain | 2.079662356 |
| Importance | 2.199188821 |
| Random | 0.735640177 |
| Cheapest | 1.104558083 |
| All-HOLD | 0.075749801 |

Total runner-stage time including exact replay and reporting was 24.457152006 seconds. Runtime was measured on Python 3.11.16. The decision-value implementation took about 2.8× the comparator's policy time in this execution. These are noisy single-run timings, not a hardware-independent complexity bound or physical energy measurement.

## Evidence package

Evaluation artifact: [exp063-35452857186](https://github.com/safal207/morphomatter/actions/runs/35452857186/artifacts/10587890320), artifact ID `10587890320`.

It contains `summary.json`, `endpoints.json`, `records.jsonl`, and `runtime.json`. The GitHub artifact retention setting is 30 days; the code and recorded summary remain in Git history, and the full traces can be regenerated. Do not assume the hosted ZIP link remains available indefinitely.

| Object | SHA-256 |
|---|---|
| Scientific source set | `00ca001fc114d63e2e1b793f4195ff2609b3607e69ae8d774136c70e7f0c1ef3` |
| Canonical manifest | `fb01893ec23cf7d6bee916fc1f9f601a2ddf091c78c72f350cf3db804a92d77d` |
| Canonical comparator lock | `80acc71b00750512b2f806dd36cce20611d10d50096a701c124798c8dca4d7a3` |
| Evaluation records.jsonl bytes | `65bfb10e4897825c6d64d9b331e3492e73b47990c53a88906e2b55efdc1c2c6b` |
| Evaluation ZIP bytes | `da2b1b3b1541138dd2fa13a293680d29fa87929ac86f318781326cc897e9c4cb` |

After downloading the evaluation ZIP outside CI, its hash, all 768 record chains, endpoint totals, per-policy mean losses, wrong counts, and budget bounds were checked against the summary. This is an additional artifact-integrity check, not an independent reproduction of the scientific model.

## Reproduce and review

From the evaluation checkout or a later docs-only descendant:

```bash
python -m unittest discover -s tests -v
python -m experiments.exp063 --stage evaluation --lock experiments/exp063_comparator_lock.json --output out/evaluation --replay
```

The new code requires only the Python standard library. Main and the prior material-experiment branches were not merged or modified by this implementation.

## Remaining boundary

Full scope-split diagnosis, unknown omitted mechanisms, adversarial regime-shift evaluation, general proof-DAG repair, large-scale two-step selection, and integration with real MorphoMatter material dynamics are not implemented here. Existing tests for scope mismatch and stale-source rejection must not be presented as completion of those scientific features.

Next engineering priority: independent review of this pilot and a separately frozen two-step/dependence stress extension using new evaluation worlds. Do not tune on these 128 worlds and relabel the same data as unseen.
