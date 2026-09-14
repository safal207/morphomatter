# Experiment 058 — Value of Proof / Experiment Portfolio Optimization

## Goal

Move from selecting one useful experiment at a time to selecting a portfolio of experiments whose combined evidence maximizes future scientific and control value under a bounded budget.

The central question is:

> Which proofs are worth obtaining now because they reduce uncertainty, improve control, strengthen multiple downstream claims, and reduce future revalidation cost?

## Core principle

Each external proof can reduce the cost of the next unit of trust, but proofs differ in leverage.

For an experiment `e`, define a bounded synthetic value model:

\[
V(e)=IG(e)+ControlValue(e)+FutureTrustSavings(e)+RepairValue(e)-Cost(e)-Risk(e)
\]

where:

- `IG(e)` is expected information gain;
- `ControlValue(e)` is expected improvement in intervention quality;
- `FutureTrustSavings(e)` is expected reduction in verification burden for downstream claims;
- `RepairValue(e)` is expected value if part of the proof graph later becomes stale or falsified;
- `Cost(e)` is experimental/intervention cost;
- `Risk(e)` captures fragility, confounding, or dependence on narrow assumptions.

The portfolio objective is not simply the sum of individual values because experiments can overlap, depend on one another, or provide redundant evidence.

\[
P^*=\arg\max_{P\subseteq E}
\Big[
JointValue(P)-Redundancy(P)-DependencyRisk(P)
\Big]
\]

subject to:

\[
Cost(P)\leq B
\]

where `B` is a fixed experiment budget.

## Why this extends Experiments 053–057

Experiments 053–057 established:

1. information-seeking experiment selection;
2. switching between discovery and control;
3. proof-carrying control;
4. proof dependency graphs;
5. minimal revalidation after proof failure.

Experiment 058 asks a new question:

> Can the system proactively acquire evidence that is useful across multiple future branches before those branches are individually requested?

This turns experiment selection into proof infrastructure design.

## Architecture

```text
Current proof graph
        ↓
Uncertain claims + future control goals
        ↓
Candidate experiments
        ↓
Estimate marginal proof value
        ↓
Estimate overlap / dependency / repair leverage
        ↓
Portfolio optimizer
        ↓
Selected experiment set
        ↓
Evidence execution
        ↓
Proof graph update
        ↓
Future trust / control / repair cost update
```

## Proof value dimensions

### 1. Information value

How much uncertainty does the experiment remove?

\[
IG(e)=H(M)-\mathbb{E}[H(M\mid outcome(e))]
\]

### 2. Control value

How much does the experiment improve future decisions?

Example metrics:

- lower intervention effort;
- fewer failed actions;
- lower target miss rate;
- better unreachable-target detection.

### 3. Trust leverage

One proof may support several downstream claims.

If proof `p` is used by claims `c_1,...,c_k`, define a simple leverage term:

\[
L(p)=\sum_i w_i\cdot DependencyStrength(p,c_i)
\]

High leverage is useful, but excessive concentration creates a single point of epistemic failure.

### 4. Repair leverage

A strategically chosen independent proof may create an alternate path through the proof graph.

```text
Claim C
 ↗    ↖
P1     P2
```

If `P1` later fails, `P2` can preserve part of the claim without replaying the full history.

### 5. Diversity value

Two independent mechanisms that support the same conclusion can be more valuable than two near-duplicate measurements of the same mechanism.

The optimizer should reward:

- independent causal paths;
- different observables;
- different perturbation families;
- different scales;
- different initial conditions.

## Portfolio interactions

Individual proof value is not additive.

### Complementarity

Two experiments may be weak alone but jointly identify a mechanism.

\[
V(e_i,e_j)>V(e_i)+V(e_j)
\]

### Redundancy

Two experiments may provide nearly the same information.

\[
V(e_i,e_j)<V(e_i)+V(e_j)
\]

### Dependency

An experiment may only be meaningful if another proof is already valid.

### Fragility concentration

A portfolio that routes many claims through one proof may be efficient now but expensive to repair later.

## Experimental design

Construct a synthetic proof graph with:

- multiple candidate causal models;
- multiple future control tasks;
- multiple downstream claims;
- experiment costs;
- overlapping evidence;
- hidden proof dependencies;
- possible future regime shifts.

Compare the following strategies under identical budgets:

1. **Greedy information gain** — choose the highest immediate IG.
2. **Greedy control value** — choose the experiment that most improves near-term control.
3. **Cheapest-first** — maximize count of proofs.
4. **Random portfolio** — matched total cost.
5. **Independent-diversity portfolio** — reward evidence-path diversity.
6. **Proof-value portfolio** — optimize combined scientific/control/trust/repair value.
7. **Oracle upper bound** — allowed only as a synthetic benchmark, never as a practical controller.

## Regime-shift test

After the portfolio is selected and used successfully, perturb one important assumption or mechanism.

Then measure:

- number of invalidated claims;
- number of proofs that remain usable;
- minimal revalidation cost;
- control degradation;
- time/steps to restore valid operation.

A robust portfolio should degrade gracefully rather than collapse because one central proof failed.

## Core metrics

### Portfolio utility

\[
U(P)=KnowledgeGain+ControlGain+TrustSavings+RepairSavings-Cost
\]

### Trust cost reduction

Total verification work required for downstream claims before vs. after the portfolio.

### Repair cost

Cost of restoring target claim validity after injected proof failure.

### Coverage

Fraction of relevant future claims and control decisions supported by valid evidence.

### Proof concentration

How much total downstream authority depends on the most central proof node.

### Evidence diversity

Number and quality of independent proof paths.

### Invalid-trust leakage

Fraction of decisions that continue using stale or falsified evidence.

Target:

```text
invalid_trust_leakage = 0
```

## Success criteria

Experiment 058 is positive only if, under matched total cost, the proof-value portfolio improves several dimensions at once, for example:

- comparable or better causal identification;
- comparable or better control;
- lower future verification cost;
- lower repair cost after proof failure;
- no increase in invalid-trust leakage.

A result that only improves one metric while degrading the others should be reported as mixed.

## Negative and null outcomes

Valid bounded outcomes include:

```text
PORTFOLIO_OPTIMIZATION_NO_GAIN_OVER_GREEDY
```

```text
REDUNDANCY_PENALTY_HURTS_IDENTIFICATION
```

```text
DIVERSITY_VALUE_NOT_OBSERVED
```

```text
FUTURE_TRUST_SAVINGS_NOT_PREDICTIVE
```

```text
REPAIR_VALUE_TOO_SPECULATIVE_TO_HELP
```

```text
PROOF_CONCENTRATION_DOMINATES_SHORT_TERM_EFFICIENCY
```

```text
BUDGET_TOO_SMALL_FOR_PORTFOLIO_ADVANTAGE
```

Negative results are part of the evidence and must not be reframed as success.

## Evidence packet

Each selected experiment should emit a replayable record:

```text
experiment_id
candidate_models_before
expected_information_gain
expected_control_value
expected_trust_savings
expected_repair_value
expected_cost
expected_risk
selected_portfolio_id
observed_outcome
proofs_created
claims_supported
independent_paths_created
posterior_update
actual_control_gain
actual_trust_savings
actual_repair_value_if_triggered
status
```

This allows predicted proof value to be compared with realized proof value.

## Calibration test

A central test is whether predicted proof value is calibrated.

The system should learn when it consistently overestimates:

- information gain;
- future trust savings;
- repair value;
- control utility.

A useful portfolio optimizer must improve its own value estimates rather than only optimize a fixed, wrong scoring function.

## Relation to the MorphoMatter principle

The project principle:

> Every external proof reduces the cost of the next unit of trust.

Experiment 058 adds:

> Some proofs reduce future trust cost much more than others, and a diversified proof portfolio can be more robust than a single high-leverage chain.

## Claim boundary

This experiment is a synthetic decision framework for MorphoMatter research planning.

It does **not** demonstrate:

- autonomous real-world materials discovery;
- real laboratory cost savings;
- physical proof of a new material law;
- universal economics of scientific evidence.

Those claims require calibrated physical experiments and independent replication.

## Next experiment

### Experiment 059 — Epistemic Resilience / Adversarial Proof Graph

Deliberately inject misleading but internally consistent evidence, confounded measurements, stale proofs, and correlated failures into the proof graph.

Question:

> Can the system detect when a seemingly strong portfolio is only giving the illusion of independent confirmation?

The central distinction becomes:

\[
Many\ proofs \neq Independent\ proofs
\]

and the goal is to measure resistance to correlated epistemic failure.
