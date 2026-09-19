# Experiment 063B — Pair lookahead, review findings, and reproducibility

## Result and interpretation

**Implemented and executed. Frozen benchmark label: `PAIR_LOOKAHEAD_MIXED_OR_NO_GAIN`.**

The pair policy resolves the analytical complementary-test example, but this implementation has **no established overall advantage** on the frozen new-world benchmark. Its observed wrong-definitive count is higher than both principal comparison policies. Keep the original policy available; this result does not justify replacing it by default.

The review also exposed receipt/world identity weaknesses and a numerical reproducibility boundary. These are concrete software findings, not physical discoveries. This remains a known-likelihood diagnostic fixture, not an integrated material simulator.

## Provenance

| Item | Reference |
|---|---|
| Original 063 pilot snapshot | `4089790a98897ab205efaba693b11c50c4600ef3` |
| 063B scope freeze before implementation/results | `fedd016449c1dc447f9911f22c5a980452b6174e` |
| First full implementation and evaluated checkout | `42262f23c9d1c47e9ab38db293d36db0c1fcf1c5` |
| 063B CI run | [35454054825](https://github.com/safal207/morphomatter/actions/runs/35454054825) — SUCCESS |
| 063B job | `105926113670` |
| Original 063 workflow at the same checkout | `35454054878` — SUCCESS |
| Evaluation runtime | Python `3.11.16` |
| Review/extension PR | [draft PR #14](https://github.com/safal207/morphomatter/pull/14), stacked on draft PR #13 |

The original evaluated 063 source files, manifest, comparator lock, and archived result files are unchanged. The new workflow passed **50 tests: 28 original + 22 extension tests**, then evaluated 128 new worlds (`2000..2127`) with seven policies. Each of the **896 policy/world records** was generated twice in CI with **zero within-runtime replay mismatches**. The statistical unit is a whole world, not individual decisions or reports.

The protocol and code were not tuned after viewing these results. Post-result portability and numeric-kernel checks below are explicitly exploratory diagnostics, not a new confirmatory study or replacement of the frozen result.

## What was actually added

Nonadaptive singleton/pair scoring uses exact expected terminal Bayes-risk reduction divided by the full listed cost of the singleton/pair. Pairs must have distinct sources and fit remaining cost and execution-step budgets. The first experiment is dispatched and all choices are reconsidered after the actual observation.

This is **not** a complete outcome-adaptive Bellman tree or full-horizon optimal control. Replanning can abandon the second experiment. Singleton scoring uses a different numerical kernel from archived 063; see the caveat below before interpreting this as a pure horizon ablation.

All policies share the same guarded runner. Receipt experiment/source/scope must match the dispatched candidate; scope is namespaced by world; blocked sources are excluded; candidate bit types are checked; step-limit reasons are explicit. Clean-fixture tests require legacy policy endpoints to match the archived runner.

## Frozen held-out benchmark

Each policy makes 3,072 terminal decisions (128 × 24). The shared budget ceiling is 12 synthetic cost units per world; actual spending can differ. Weighted loss is 0 for a correct definitive decision, 1 for HOLD, and 10 for a wrong definitive decision, multiplied by fixed task weights 1 or 3.

| Policy | Mean weighted loss/world | Total loss | Correct | Wrong definitive | HOLD | Mean cost |
|---|---:|---:|---:|---:|---:|---:|
| Pair value | 19.1484375 | 2451 | 2383 | 70 | 619 | 11.8906250 |
| One-step decision value — primary comparator | 19.6250000 | 2512 | 2326 | 62 | 684 | 11.9687500 |
| Information gain — descriptive secondary | 21.3828125 | 2737 | 2335 | 68 | 669 | 11.5156250 |
| Importance | 29.1015625 | 3725 | 1705 | 58 | 1309 | 11.6093750 |
| Random | 29.2187500 | 3740 | 1636 | 48 | 1388 | 12.0000000 |
| Cheapest | 32.4218750 | 4150 | 1296 | 36 | 1740 | 11.5703125 |
| All-HOLD | 48.2031250 | 6170 | 0 | 0 | 3072 | 0 |

### Primary, frozen before evaluation

`loss_one_step - loss_pair`:

- mean: **0.4765625** units/world;
- two-sided 95% paired whole-world bootstrap interval: **[-1.828125, 2.711328125]**;
- bootstrap: 10,000 resamples, seed `63060`;
- pair has lower loss in 27 worlds, equal loss in 88, and higher loss in 13;
- wrong-definitive count: **70 versus 62** — the no-higher-wrong-count gate fails.

The roughly **2.43%** lower mean loss is a point estimate, not an established gain. Both the interval criterion and the error-count guard prevent a positive verdict. Lower mean loss and more errors are compatible because HOLD and task importance are also part of the loss function.

### Secondary, descriptive only

Against information gain, the mean loss difference is **2.234375**, with interval **[-1.0861328125, 5.8830078125]**. Pair has 70 wrong definitive decisions versus 68. This is not a positive replication of an advantage either. No post-hoc switch to a weaker comparator was made.

## Useful mechanism result versus general performance

In the exact toy case `sensor = claim XOR fault`, a perfect fault audit and a perfect sensor are useless individually for the symmetric one-step decision problem but useful jointly. The pair policy executes both and obtains the correct answer for all 16 latent hypotheses; one-step decision value stays at HOLD. Joint risk calculations also match explicit noisy two-observation posterior enumeration.

That establishes this bounded mechanism and the scoring implementation, **not** a universal benefit. In the benchmark, pair plans were selected 61 times across 50 worlds. That count is not the number of independent successful discoveries.

## Review defects reproduced and contained in the extension

The new regression suite demonstrates that v1 can accept a valid packet for an experiment different from the one just purchased. The extension rejects it before posterior update. Tests also cover cross-world packet reuse, unseen revoked sources, bool/float bit coordinates, and incorrect step-limit metadata. Details: [review and protocol](EXPERIMENT_063B_REVIEW_AND_PROTOCOL.md).

All benchmark policies have zero observed budget violations, known-invalid evidence-use detections, mismatched receipt rejections, or invalid record chains under the clean generator. The deliberately injected negative tests reject invalid packets. These zeros do not mean that scientific decisions are all correct; the wrong-decision column is essential.

Review was performed by the same assistant using fresh tests. **External independent review has not occurred.**

## Computational cost

Measured policy execution time for all 128 worlds, excluding replay, on this one CI runner:

| Policy | Seconds |
|---|---:|
| Pair value | 1.772909463 |
| One-step decision value | 3.707215136 |
| Information gain | 1.280731028 |
| Importance | 1.408997679 |
| Random | 0.449905195 |
| Cheapest | 0.697616857 |
| All-HOLD | 0.062157071 |

The full evaluation stage including replay took 19.490648712 seconds. The pair implementation uses cached unnormalized-mass calculations; the original one-step implementation uses repeated posterior calculations. Therefore these observed timings compare implementations, not equal-optimization asymptotic algorithm costs. The pair implementation was faster than the original one-step implementation in this execution, but slower than information gain. No physical energy claim follows.

## Additional finding: cross-version replay is not exact

The artifact was downloaded and its ZIP SHA-256, source-file hashes, all 896 ledger chains, receipt bindings, cost reservations, terminal losses, and aggregate metrics were checked separately. All of those checks passed.

The source snapshot was then run in the local Python **3.13.5** environment. All **50 unit tests passed there too**, but exact full-record comparison against CI Python 3.11.16 failed:

- exact record matches: **0/896** (floating posterior values/hash chains differ);
- endpoint matches: **873/896**;
- changed endpoints: 21 information-gain records and 2 one-step decision-value records;
- pair-value endpoints: **128/128 match**, although selected action sequences match in only 122/128 worlds;
- information-gain total loss: CI 2737 versus local 2774;
- one-step decision-value total loss: CI 2512 versus local 2520;
- pair-value total loss: 2451 in both.

This is not just a hash-format difference: some experiment selections and terminal outcomes change. The first recorded numeric difference is a posterior probability `0.21799999999999992` versus `0.21800000000000003`. Policies sort floating-point scores with exact-score ties, so tiny numerical changes can alter later experiments.

Python's official documentation records a change to float summation in Python 3.12: [built-in sum, Python 3.13 documentation](https://docs.python.org/3.13/library/functions.html#sum).

A **post-hoc, in-memory diagnostic** replaced module-level `sum` calls in the two model modules by simple sequential addition while staying on Python 3.13.5. Without changing any source files, that diagnostic matched all **896/896** CI records exactly. This isolates a summation-behavior explanation for these tested discrepancies. It is **not** an actual second Python 3.11 interpreter run, external replication, or a retroactive scientific code fix.

Consequently, the frozen numbers above are explicitly Python-3.11.16 results. Until numerical policy is versioned and tested, do not promise exact cross-version reproducibility merely because code and RNG seeds match.

## Additional caveat: horizon and numerical kernel are not fully isolated

The pair scorer uses unnormalized masses and `math.fsum`, while the archived one-step scorer uses normalized posteriors and built-in `sum`. The formulas agree mathematically and pass exhaustive checks, but their machine-precision rankings can differ.

A post-result trace check found **11 worlds where pair_value selected no pair at all yet followed a different action sequence than decision_value**; one of those worlds has a different terminal loss. This prevents interpreting every observed difference as caused only by looking two experiments ahead.

For a clean horizon-only comparison, both horizons must use the same numeric kernel and an explicitly frozen near-tie policy. That is a next-version requirement, not a change made after seeing this benchmark.

## Artifacts and persistence

Full CI artifact: [exp063b-35454054825](https://github.com/safal207/morphomatter/actions/runs/35454054825/artifacts/10587602047), artifact ID `10587602047`, 30-day configured retention.

Contains `summary.json`, all `endpoints.json`, full `records.jsonl`, `runtime.json`, manifest, source hashes, exact tracked-source snapshot ZIP, and unit/evaluation logs.

| Object | SHA-256 |
|---|---|
| CI ZIP | `ab2b91becf2c568308927706fb51ddc62ebe7302e85ce41449e0ae838d99aff9` |
| Complete records.jsonl | `101a0a6b09b1a515ef209f299133a4a6cbf26681533c5420daa3fb5b1d422144` |
| Evaluated source set | `6a72524417e19bb7faacbd5adfb308a2b35f922af8ca19e8963c1504f9fb76fa` |
| 063B protocol | `95a186b3c8217bfdfb7ae6b1520b25d784198e66a5fe9c019d5b109fb7d2bdd9` |
| Archived 063 scientific source set | `00ca001fc114d63e2e1b793f4195ff2609b3607e69ae8d774136c70e7f0c1ef3` |

Persisted summary and verification notes are in `results/exp063b/`. Artifact retention does not guarantee indefinite download availability. Hash integrity does not certify the model's empirical truth.

## Next engineering priority

Keep the receipt/budget guard improvements. Before increasing planning depth or claiming an AI benefit, freeze a common numeric risk kernel, deterministic near-tie handling, and a Python-version reproducibility matrix. Then compare horizons on new worlds. Do not tune on worlds `2000..2127` and call them unseen again.

No scientific source file was changed after this result. Main and the parent PR's branch were not merged or modified by the extension.
