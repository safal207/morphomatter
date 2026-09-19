# Experiment 063B — Review and two-experiment lookahead

## Status

Implementation/protocol extension of the executable 063 pilot. No result is assigned by this document. The original implementation, comparator lock, and archived results are preserved unchanged.

Base reviewed: `4089790a98897ab205efaba693b11c50c4600ef3` (draft PR #13).

063B scope freeze: `fedd016449c1dc447f9911f22c5a980452b6174e`, before implementation and 063B evaluation results.

This review is a fresh code inspection and new tests by the same assistant, **not** external independent review or cross-laboratory replication.

## Review findings

### R1 — A valid receipt is not necessarily the selected experiment's receipt

The archived `run_policy` passes the returned receipt straight to `EvidenceStore.ingest`. That verifier checks against *a* registered candidate, not specifically the candidate just reserved in the budget ledger. A faulty adapter can return a valid high-cost experiment's packet while the scheduler paid only for a different low-cost experiment.

New regression test 11 demonstrates the old behavior and verifies the guard: match experiment ID, source ID, and scope against the dispatched candidate **before** ingesting. Reject with `RECEIPT_DISPATCH_MISMATCH`; keep the charged cost and preserve unrelated valid evidence.

The stock `World.observe` returns the selected candidate correctly, so this is an exposed runner-contract weakness, not evidence that the published clean-world loss table was corrupted.

### R2 — Source/scope identity repeats between synthetic worlds

The base generator reuses group/source IDs and scope strings for different world seeds. That is sufficient for isolated in-memory fixtures but cannot authenticate a packet's world of origin. A copied packet can pass the base verifier in another world.

063B binds candidate/receipt scope to an opaque world namespace, without changing the measurement RNG key or latent model. Tests 13 and 14 distinguish the new guard from the old contract. This is not cryptographic sender authentication or protection against a caller that can forge all fields.

### R3 — An unseen invalidated source remains selectable

`invalidate` marks a source blocked, but the archived selector input combines attempted and dispatched sources only. A source revoked before its first observation can still be selected, consuming budget although its returned evidence is quarantined.

063B excludes blocked sources at the common scheduling boundary; test 15 covers the unseen case. Existing observed-source invalidation tests do not cover it.

### R4 — Candidate bit type validation is weaker than Task validation

Python membership in `range(3)` accepts `True` and `1.0`. A floating bit can later fail in a bit shift, while bool silently aliases an integer. The extension rejects both before scheduling (test 16), without changing the archived v1 module.

### R5 — Step-limit exit can retain a selection reason

The old runner can return a policy label when the for-loop naturally exhausts. The extension records `STEP_LIMIT` explicitly (test 20). No clean-world superiority claim depends on this metadata repair.

## What changes scientifically

The first policy maximizes immediate expected decision-risk reduction per cost. The extension adds candidate **pairs**:

`pair_score(a,b) = [R(D) - E_y_a,y_b R(D + observations)] / [cost(a) + cost(b)]`.

Singletons remain eligible. Candidate pairs must use distinct information sources, fit the remaining budget, and fit the remaining number of execution steps. Conditional dependence through the declared shared fault is retained in the joint likelihood. Different independent groups have additive expected gains.

The first member of the highest-scoring plan is executed, then all scores are recomputed from its actual result. This is nonadaptive pair scoring plus receding-horizon execution. It is **not** a fully adaptive depth-two decision tree, a full-horizon optimum, or proof that pair search must outperform greediness. Replanning may abandon the anticipated second experiment.

For efficient scoring, risk is evaluated on unnormalized posterior masses, and only the three state-independent failure labels are combined. Execution preserves each separate label. Test 03 compares this calculation against explicit two-stage outcome/posterior enumeration with noisy and failed observations. A perfect XOR sensor plus fault audit supplies an analytical complementary pair: either alone has zero immediate decision value; together they resolve the bit.

## Fair comparison

All seven policies use the same guarded runner. The original six policy endpoint results must remain unchanged on the clean smoke worlds (test 17); archived code and result files are not edited. The two-step extension is a new version, not a retuning of the published 128 worlds.

Evaluation: 128 new worlds `2000..2127`; smoke only `200..202`; no hyperparameter tuning or new comparator selection. Primary comparator is original `decision_value` (isolates the pair-search increment); `information_gain` is a fixed descriptive secondary comparator. Budget, loss weights, likelihoods, initial observations and generator remain the same as v1.

The manifest specifies whole-world paired bootstrap intervals, a no-higher observed wrong-decision count gate, integrity gates, and honest mixed/null outcomes. Runtime and abstention are reported alongside loss. Different policies share a budget ceiling; realized spending can differ.

## Run and evidence

```bash
python -m unittest discover -s tests -v
python -m experiments.exp063b --stage smoke --output out/063b-smoke --replay
python -m experiments.exp063b --stage evaluation --output out/063b --replay
```

The dedicated workflow records all test logs, complete selection/receipt traces, per-world endpoints, source hashes and a tracked-source snapshot ZIP. An exact replay or artifact-hash check is software repeatability, not independent confirmation of the model family.

## Remaining limits

Known finite diagnostic likelihoods, known source groups, and synthetic cost/loss only. No material dynamics, real laboratory, causal-law discovery, adversarial unknown-law batch, or physical energy estimate. The new negative controls establish particular API/algorithm properties, not that all possible adapter faults are detected.

Next acceptance gate: inspect the actual 063B result and its costs. Do not create another numbered roadmap as a substitute for this evaluation.
