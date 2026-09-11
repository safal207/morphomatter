# Experiment 009 preregistration addendum — training-seed correction

Status: **FROZEN BEFORE FIRST EXPERIMENT 009 RESULT**

The initial Experiment 009 preregistration contains one internal inconsistency: it requires the Experiment 008 original-rich curve to reproduce exactly, while also naming a new per-lambda training seed `9009 + int(lambda * 100)` for both learners.

Exact causal isolation requires the original-rich learner to use the **same training seed as Experiment 008**. Therefore, before any Experiment 009 scientific run, freeze the following correction:

- `rich_original` training seed at each lambda: `8008 + int(lambda * 100)`;
- `rich_expanded` training seed at each lambda: **the same** `8008 + int(lambda * 100)`.

This correction removes a confound and preserves the intended single experimental variable: the action map.

No action definition, lambda value, transition-law parameter, state feature, damage geometry, held-out seed, reward term, training episode count, goal, horizon, or interpretation threshold is changed by this addendum.

The original preregistration remains part of the provenance record and is not edited after the fact.