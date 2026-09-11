# Experiment 007 — controllability boundary results

## Provenance

The protocol was frozen before any boundary-matrix result was observed:

- preregistration commit: `9ce8b94614707c098a36d7fa9f68aecbaa237d04`;
- undefined-boundary addendum commit: `71ebee1b87e4cdce1966a8908f278c77ce17d3f6`.

The first CI attempt did **not** execute Experiment 007 because a unit test detected floating-point endpoint drift (`0.0019999999999999983` vs `0.002`). The implementation was corrected to return exact frozen endpoints at lambda `0` and `1`; no lambda, seed, geometry, training setting, comparator, success threshold, or interpretation rule was changed.

The first completed Experiment 007 boundary matrix ran on implementation head:

`36db2803b9fa3553dda9cee03298f28d3c58d71f`

GitHub Actions push run:

`34565384348`

The workflow passed unit tests and Experiments 002–007.

## Frozen matrix result

| lambda | learned success | cooperative success | brute success | random success |
|---:|---:|---:|---:|---:|
| `0.00` | `49/64` (`0.765625`) | `57/64` (`0.890625`) | `14/64` (`0.218750`) | `416/512` (`0.812500`) |
| `0.20` | `46/64` (`0.718750`) | `49/64` (`0.765625`) | `1/64` (`0.015625`) | `371/512` (`0.724609`) |
| `0.40` | `42/64` (`0.656250`) | `42/64` (`0.656250`) | `1/64` (`0.015625`) | `324/512` (`0.632812`) |
| `0.60` | `38/64` (`0.593750`) | `38/64` (`0.593750`) | `0/64` (`0.000000`) | `263/512` (`0.513672`) |
| `0.80` | `32/64` (`0.500000`) | `33/64` (`0.515625`) | `0/64` (`0.000000`) | `174/512` (`0.339844`) |
| `1.00` | `16/64` (`0.250000`) | `16/64` (`0.250000`) | `0/64` (`0.000000`) | `69/512` (`0.134766`) |

All reported transition traces replayed exactly.

## Frozen boundary metric

Using the preregistered definition `lambda50 = maximum tested lambda with success_rate >= 0.50`:

- learned: `0.80`;
- cooperative heuristic: `0.80`;
- brute force: `NONE`;
- random: `0.60`.

The preregistered separation-point condition was **false** because at the learned boundary (`lambda=0.80`) the cooperative heuristic was also still above 50% success (`33/64 = 0.515625`).

Frozen result label:

`CONTROLLABILITY_BOUNDARY_OVERLAP`

## What the result supports

The experiment identifies a non-saturated transition region between the earlier easy and impossible regimes. Random control falls below the 50% boundary before learned/cooperative control:

`random lambda50 = 0.60 < learned/cooperative lambda50 = 0.80`.

So structured condition selection matters in this toy model.

However, the learned policy does **not** shift the preregistered controllability boundary beyond the fixed cooperative heuristic. The supported capability observation is therefore about **structured cooperative control versus random/brute control**, not an AI-specific boundary shift.

## Descriptive effort observation

Although not part of the boundary-shift pass/fail rule, the learned policy generally used less declared control effort than the cooperative heuristic among successful runs. Examples:

- lambda `0.60`: learned median effort `1.610` vs cooperative `2.090`;
- lambda `0.80`: learned median effort `1.795` vs cooperative `2.280`;
- lambda `1.00`: learned median effort `2.035` vs cooperative `2.280`.

This is consistent with Experiment 005's lower-effort signal, but it does not change the Experiment 007 capability label.

## Key interpretation

The current software evidence now separates three facts:

1. **Experiment 005:** in an easy/saturated regime, learned control reduces declared intervention effort.
2. **Experiment 006:** in an over-hard regime, no tested controller succeeds.
3. **Experiment 007:** across the frozen boundary curve, learned and cooperative control reach the same `lambda50`, while random control crosses the 50% boundary earlier.

The next model question is therefore not simply "use a larger AI." A stronger experiment should ask what missing state information or action expressivity prevents the learned policy from outperforming the cooperative heuristic near the boundary.

## Non-claims

Experiment 007 does not establish a real material phase boundary, physical self-repair, physical energy efficiency, or general AI superiority. `lambda`, success, and effort are dimensionless software quantities.