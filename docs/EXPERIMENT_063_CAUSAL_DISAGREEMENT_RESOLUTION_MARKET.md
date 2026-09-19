# Experiment 063 — Causal Disagreement Resolution Market

## Status and scope

**Status: DRAFT_PROTOCOL. Implementation: NOT_IMPLEMENTED by this change. Execution: NOT_RUN. Results: NONE.**

This document records a proposed synthetic benchmark, not a completed experiment, a frozen result, or a physical discovery. A protocol-freeze commit and an executable benchmark are required before collecting confirmatory results. The term `market` means allocation of a bounded experimental budget; it does not mean financial trading, tokens, bidding for scientific truth, or voting.

The immediate predecessor is [Experiment 062 — Federated Claim Consensus Without Majority Voting](EXPERIMENT_062_FEDERATED_CLAIM_CONSENSUS_WITHOUT_MAJORITY_VOTING.md). Related designs are [058 — proof portfolio optimization](EXPERIMENT_058_VALUE_OF_PROOF_PORTFOLIO_OPTIMIZATION.md), [060 — replication allocation](EXPERIMENT_060_INDEPENDENT_REPLICATION_ALLOCATION_PROOF_DECORRELATION.md), and [057 — proof repair](EXPERIMENT_057_MINIMAL_REVALIDATION_PROOF_REPAIR.md). These are design dependencies here, not assertions that their implementations or results exist.

`Proof` retains the project's evidence-packet terminology. Empirical or simulated support is not a mathematical proof. Hashes establish artifact identity, not the truth of a scientific claim.

## Question

Given several unresolved, partially dependent disagreements and a fixed budget, can a dependency-aware scheduler choose experiments that reduce consequential decision errors more effectively than cheapest-first, random, or information-gain-only selection?

The scheduler chooses **what to investigate next**, not **which result must be true**.

Resolving a disagreement can mean supporting a bounded claim, falsifying it within scope, identifying a scope split, diagnosing a measurement failure, or establishing non-identifiability. It does not require agreement or a favorable material-control outcome.

## Material-facing example

Suppose simulated domains disagree about whether an interaction window permits recovery. Competing explanations are a shared screening implementation error, a calibration offset, different initial histories, or a genuinely scope-dependent transition.

One calibration audit might resolve several affected comparisons. Repeating twenty runs through the same implementation might add little information about that common error. Conversely, a new seed can be useful for estimating stochastic variation even though it does not independently test the implementation.

These are proposed test cases, not observed results. No external laboratory has participated in this experiment. The scheduler operates on synthetic measurements or audits; it cannot directly alter a claimed `causal field` or authorize physical hardware.

## Separate priority, evidence, and authority

Three components must remain separate:

1. **Scheduler:** ranks feasible experiment candidates using estimated downstream value and cost.
2. **Evidence verifier:** checks provenance, scope, dependencies, measurement validity, and the versioned evidence policy.
3. **Claim evaluator:** updates bounded claim statuses using verified observations, not the experiment's priority score.

The scheduler may not rewrite ground truth, change a claim's acceptance threshold, delete inconvenient outcomes, mark a stale packet valid, or grant itself execution authority.

```text
Disagreement registry + evidence dependency graph
                    |
                    v
        Candidate audits / measurements
                    |
                    v
       Feasibility and budget checks
                    |
                    v
         Expected decision-value estimate
                    |
                    v
             Select experiment
                    |
                    v
      Execute in the synthetic test harness
                    |
                    v
     Verify observation, provenance and scope
                    |
                    v
     Update claims, dependencies and remaining budget
```

## Data contracts

A disagreement records:

```text
disagreement_id
claim_ids and claim_versions
conflict_class
competing_explanations
scope: material, environment, interface, geometry, history, scale, horizon
supporting_evidence_ids
contradicting_evidence_ids
shared_dependency_ids
independence_assumptions and unknown_dependencies
blocked_decision_ids
current_status
```

A candidate experiment records:

```text
experiment_id and protocol_version
disagreement_ids_addressed
proposed_observable_or_intervention
scope_tested
required_valid_dependencies
expected_outcome_distribution_by_hypothesis
measurement_and_failure_model
trust_domain_vector
expected_new_information_source
cost_units and cost_upper_bound
execution_preconditions
stopping_rule
```

A task/decision registry assigns stable IDs and explicit loss weights. If the same downstream task depends on five disagreements, its value is counted once, not five times. Dependencies distinguish required joint support from alternative independent support paths.

Unknown independence remains `UNKNOWN`; different filenames, agents, or lab labels are not sufficient evidence of independence. A scope split requires an explicit separator and supporting observations, not a convenient post-hoc label.

## Objective: decision value, not conflict popularity

The earlier sketch `ExpectedUnlockedValue * ConflictSeverity / Cost` is a hypothesis for a baseline, not a validated law. Multiplying importance terms can count the same consequence twice.

For a proposed decision-theoretic implementation, let:

- `D_t` be the evidence actually observed by time `t`;
- `Theta` describe competing mechanisms, measurement faults, and scope hypotheses;
- `A` be the fixed decision vocabulary, including `HOLD`;
- `L(a, Theta)` be the preregistered loss over **unique** downstream tasks.

Define the current model-estimated decision risk:

\[
R(D_t)=\min_{a\in A}\mathbb{E}[L(a,\Theta)\mid D_t].
\]

For a feasible candidate `e`, estimate:

\[
\Delta(e\mid D_t)=R(D_t)-\mathbb{E}_{y\sim p(y\mid e,D_t)}[R(D_t\cup\{(e,y)\})].
\]

The predictive outcome distribution must include inconclusive observations, measurement failure, and relevant shared-error hypotheses. This expectation is an estimate under the chosen model class, not knowledge of the hidden evaluator truth.

A bounded myopic allocation rule is:

\[
e_t^*=\arg\max_{e\in E_t^{feasible}}\frac{\Delta(e\mid D_t)}{c(e)},\qquad c(e)>0.
\]

Ties use a frozen deterministic rule. Zero-cost bookkeeping runs as a bounded preprocessing stage; no epsilon denominator is used to turn nominally free experiments into infinite priority. Uncertain execution costs reserve their declared upper bound before dispatch.

Decision loss and experiment cost have separately declared units. Information in bits, monetary cost, physical energy, and confidence scores must not be added without an explicit conversion model. The primary benchmark compares final decision loss under the same budget. Physical energy savings are out of scope.

This greedy rule is **not** claimed to be globally optimal. A complementary pair of experiments can be valuable even if each has low standalone value. Record this limitation and test a bounded two-step lookahead ablation. An exact small-instance solution may be used only with the same information available to the scheduler; an omniscient evaluator is a separate, explicitly privileged reference.

## Sequential execution rules

At each step:

1. Validate the current evidence state and remove only invalid support paths. Preserve independent valid evidence, as specified in Experiment 057.
2. Recompute which experiments are feasible under current dependencies, remaining budget, and execution preconditions.
3. Estimate marginal value from information available now. Do not inspect future observations or concealed fault labels.
4. Select and reserve one candidate. Record the prediction and selection reason before its outcome is revealed.
5. Obtain one verified observation, charge the cost, and update claim statuses through the independent evaluator.
6. Recompute priorities. Do not reuse stale pre-update values for the rest of the queue.

A failed experiment consumes its actual accounted cost and remains in the ledger. An inconclusive result is not success. A lost execution receipt gives `EXECUTION_UNKNOWN`; do not launch an unbounded automatic retry. Retry identity, duplicate detection, and budget accounting must be explicit.

Stop at the budget limit, after the maximum allowed steps, when no candidate is feasible, or when estimated decision value is non-positive. The last case means `NO_POSITIVE_EXPECTED_VALUE_UNDER_CURRENT_MODEL`, not proof that no informative experiment exists.

## Proposed bounded benchmark

Before the first confirmatory run, freeze the generator, loss table, candidate vocabulary, dependency semantics, likelihood model, selection policies, and evaluation code in a versioned protocol manifest.

Proposed v0 settings:

| Item | Proposed value |
|---|---|
| Disagreements per world | 12 |
| Unique downstream decisions | 24 |
| Candidate experiments | At most 36; a candidate may address multiple disagreements |
| Candidate cost | Positive integer units in `{1, 2, 4}` |
| Total budget per policy/world | 12 units |
| Maximum dispatched experiments | 12 |
| Development world seeds | `0..31` |
| Held-out world seeds | `1000..1127` |
| Primary endpoint | Final weighted decision loss under the common budget |
| Statistical unit | Whole synthetic world, not reports or graph nodes |

Proposed terminal loss per downstream task: `0` for a correct supported decision, `1` for withholding a conclusion, and `10` for a definitive but incorrect or out-of-scope decision. Task importance weights are `1` or `3` and are fixed by the generator. This is a declared synthetic preference, not a universal cost of scientific error. All-HOLD is a required baseline so trivial abstention cannot be presented as a discovery improvement.

The generator must specify how correct statuses and scope partitions map to downstream decisions. Public descriptors must not encode the hidden fault type. Policies see the same initial information, available candidate descriptions, and returned observations. Ground truth and future outcomes are evaluator-only.

Use independent random streams for world generation, measurement noise, and policy randomization. Common outcome tapes may pair policies only when the measurement model permits that coupling. Cloned reports are never treated as new draws. Lock the manifest and run seeds before evaluation; record post-freeze changes as amendments rather than silently retuning.

The settings above are a proposed protocol, **not evidence that these worlds have been generated or tested**.

## Required scenarios and falsification checks

| Scenario | Required distinction |
|---|---|
| Correlated confirmation | Many reports derived from one run must not inflate independent support or scheduler value. |
| Shared calibration fault | A single audit may help several conflicts; downstream benefits must be counted once. |
| Independent contradiction | One credible conflicting observation remains visible; it is not automatically true or outvoted. |
| Scope/history mismatch | A material or history difference may require `SCOPE_SPLIT`, not a universal truth/falsity verdict. |
| Complementary experiments | Two individually weak tests can jointly discriminate mechanisms; compare greedy and two-step selection. |
| Unresolvable high-impact dispute | High importance cannot manufacture identifiability under an inadequate experiment menu. |
| Misspecified model class | A concentrated posterior need not be correct; include a missing true mechanism and mismatch checks. |
| Manipulated centrality | Duplicate task/claim IDs must not create extra value or attract more budget. |
| Stale ancestor after regime change | Recompute only affected support and priorities; preserve independent evidence. |
| Cheap misleading versus costly useful test | Compare realized value, not the scheduler's self-reported utility. |
| Measurement failure / missing receipt | Account for cost without inventing a usable result or replaying automatically. |
| Everything unresolved | Report coverage and cost alongside correctness; zero conclusions is not automatic success. |

Include clean worlds as well as adversarial worlds. A benchmark containing only failures chosen to hurt simple baselines is insufficient.

## Baselines and ablations

Compare the proposed scheduler with:

- all-HOLD / no new experiments;
- random feasible selection under the same budget;
- cheapest feasible experiment first;
- greedy expected information gain per cost;
- the historical downstream-importance/conflict-severity heuristic;
- bounded two-step decision-value lookahead.

Freeze one best non-oracle comparator using development worlds only. Do not choose it using held-out performance. Report all baselines, not only the weakest.

Ablations remove dependency grouping, scope matching, shared-benefit deduplication, or uncertainty-aware value estimation one at a time. A shuffled-priority control should preserve candidate feasibility and budget. The scheduler's gain must not arise from extra measurements, privileged simulator access, or a different claim evaluator.

## Metrics and decision rule

Report final decision loss, actual spending, useful scope-correct resolution coverage, false definitive decisions, unnecessary abstention, dependency-audit cost, and end-to-end computation cost. Report calibration by comparing predicted risk reduction with realized changes in evaluator loss across worlds.

Two trust metrics must be separate:

- **Known-invalid trust leakage:** decisions that use evidence already marked stale, falsified, unresolved in execution, or outside scope by the declared policy. Target is zero in the tested harness.
- **Undetected false trust:** confident wrong decisions due to hidden faults the system did not identify. Measure empirically; a passing software invariant cannot guarantee this rate is zero in reality.

Primary paired effect is `loss_frozen_comparator - loss_proposed` for each held-out world. Proposed uncertainty report: 10,000 paired bootstrap resamples of whole worlds, seed `63059`, with a two-sided 95% percentile interval. Keep reports from a shared source in the same resampled world; do not inflate sample size with duplicated packets.

A bounded positive result requires a primary effect whose interval is entirely above zero, no known-invalid leakage or budget violation, and no higher observed false-definitive-decision rate than the frozen comparator. Also disclose coverage and computational overhead. Other comparisons are exploratory unless separately frozen. Failure to meet the rule is mixed, null, negative, or inconclusive; do not rename it success.

Possible result labels, **not assigned by this document**:

```text
DECISION_VALUE_ALLOCATION_GAIN_WITHIN_BENCHMARK
NO_GAIN_OVER_FROZEN_BASELINE
GREEDY_SELECTION_MISSES_COMPLEMENTARY_TESTS
MODEL_MISSPECIFICATION_INVALIDATES_VALUE_ESTIMATES
GAIN_REQUIRES_PRIVILEGED_INFORMATION
ABSTENTION_REDUCES_ERRORS_WITHOUT_USEFUL_RESOLUTION
KNOWN_INVALID_TRUST_LEAKAGE_DETECTED
BUDGET_OR_SCOPE_VIOLATION
INCONCLUSIVE_UNDER_FROZEN_PROTOCOL
```

Operational reasons such as `INSUFFICIENT_BUDGET`, `NEEDS_INDEPENDENT_REPLICATION`, and `CONFLICT_NOT_RESOLVABLE_WITH_AVAILABLE_EXPERIMENTS` belong to individual decisions. They are not proof that a claim is false.

## Evidence and reproducibility contract

For every selection, record:

```text
run_id, world_id, protocol_hash, code_commit, policy_version
step, budget_before, reserved_cost, actual_cost, budget_after
disagreement_ids, unique_downstream_decision_ids
candidate_set_hash, candidate_value_estimates, selected_experiment_id
selection_reason, known_dependencies, unknown_independence_flags
prediction_before_execution, admissible_outcomes, execution_identity
observed_outcome, observation_source, verification_status
claim_status_before, claim_status_after, affected_support_paths
preserved_independent_evidence, unresolved_conflicts
replay_artifact_refs, remaining_uncertainty
```

Keep evaluator-only ground truth out of planner inputs and record its access boundary. Use append-only decision records, immutable experiment identities, and content-addressed artifacts. Reproducing a scheduler trace establishes software repeatability, not external replication or a new physical law.

## Implementation handoff — not implemented here

A first executable increment should contain a small synthetic disagreement fixture, the shared verifier/evaluator, at least random and information-gain baselines, the dependency-aware scheduler, a budget ledger, and tests for duplication, scope mismatch, missing receipts, and shared-benefit accounting.

Before the full benchmark, verify on a tiny instance by exhaustive enumeration that candidate scoring uses only available information and that accounting is correct. Do not require the candidate policy to win that test; correctness and superiority are separate gates.

Keep material dynamics unchanged while isolating the scheduler. A later integration may adapt existing material simulations after their code, versions, and availability are verified. No dependency on unimplemented world models, fractal layers, autonomous laboratory tools, or all previous numbered experiments is required for the first fixture.

## Claim boundary and next action

This proposal does not demonstrate autonomous materials discovery, scientific consensus, real laboratory savings, universal truth scores, physical controllability, or new laws of nature. Independence is an exposed assumption to test, not a label the optimizer can assign to itself.

**Next action: freeze and implement this bounded benchmark, then report its actual results. Do not treat another numbered roadmap document as execution of Experiment 063.**
