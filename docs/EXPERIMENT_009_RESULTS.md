# Experiment 009 — action-space ablation results

## Provenance

Initial preregistration was committed before the first Experiment 009 result:

`edfeac8da0077aa780aee0336457424d57ccfc08`

A pre-run training-seed correction was frozen before the first result to remove an internal confound and make the old-rich baseline reproduce Experiment 008 exactly:

`a4e09f5bb39758f99423a8b571c98870ec3a266e`

The first completed Experiment 009 implementation head was:

`46664563858998a7e7c77d63663e1c95f8187cd4`

GitHub Actions push run:

`34573059632`

The run passed `31` unit tests and Experiments 002–009. The frozen Experiment 008 original-rich success curve and Experiment 007 cooperative curve reproduced exactly before the expanded-action result was interpreted.

## Frozen result

Preregistered label:

`EXPANDED_ACTION_NO_GAIN_OR_MIXED`

The 11-action rich-state learner did **not** move the 50% controllability boundary.

| Controller | lambda50 |
|---|---:|
| rich expanded actions | `0.80` |
| rich original actions | `0.80` |
| cooperative heuristic | `0.80` |

There was no preregistered separation point at which expanded-rich success was at least 50% while both original-rich and cooperative success were below 50%.

## Success curve and effort

| lambda | Expanded success | Expanded median effort | Original-rich success | Original-rich median effort | Cooperative success | Cooperative median effort |
|---:|---:|---:|---:|---:|---:|---:|
| `0.00` | `49/64` (`76.6%`) | `1.330` | `49/64` (`76.6%`) | `1.140` | `57/64` (`89.1%`) | `1.900` |
| `0.20` | `45/64` (`70.3%`) | `1.660` | `45/64` (`70.3%`) | `1.520` | `49/64` (`76.6%`) | `1.900` |
| `0.40` | `42/64` (`65.6%`) | `1.540` | `42/64` (`65.6%`) | `1.520` | `42/64` (`65.6%`) | `2.090` |
| `0.60` | `40/64` (`62.5%`) | `1.895` | `39/64` (`60.9%`) | `1.520` | `38/64` (`59.4%`) | `2.090` |
| `0.80` | `35/64` (`54.7%`) | `1.700` | `32/64` (`50.0%`) | **`1.470`** | `33/64` (`51.6%`) | `2.280` |
| `1.00` | `19/64` (`29.7%`) | `1.710` | `16/64` (`25.0%`) | `1.710` | `16/64` (`25.0%`) | `2.280` |

All expanded-policy replay failures: `0`.

## Expanded action usage

Across all held-out runs and lambdas, expanded-policy action totals were:

- `cooperate`: `2542`
- `renucleate`: `198`
- `renucleate_low_threshold`: `35`
- `stabilize_high_threshold`: `34`
- `couple_strong`: `25`
- `hold`: `16`
- `bridge_drive`: `15`
- `couple_gentle`: `12`
- `cooperate_low_threshold`: `11`
- `balanced`: `5`
- `brute`: `5`

The learner did use every added action at least once, but the original `cooperate` action remained dominant.

## Interpretation

Experiment 009 changes the global action vocabulary while holding the Experiment 008 rich observation, boundary grid, transition law, training/held-out cases, reward, Q-learning hyperparameters, training budget, goal, and horizon fixed.

The expanded vocabulary produced small descriptive success-count improvements in the harder part of the curve:

- lambda `0.60`: `40/64` vs `39/64`;
- lambda `0.80`: `35/64` vs `32/64`;
- lambda `1.00`: `19/64` vs `16/64`.

However, these gains were insufficient to move `lambda50` from `0.80` to `1.00`, so the preregistered capability criterion failed. The expanded learner also did not satisfy the preregistered effort-only criterion: at the shared boundary lambda `0.80`, median declared effort increased from `1.470` to `1.700` despite the higher success count.

Therefore this frozen test does **not** support the claim that this 11-action global vocabulary removes the Experiment 007/008 capability ceiling.

Taken together with Experiment 008, the current evidence says:

1. richer observation can reduce effort without moving the boundary;
2. this modest expansion of discrete global actions can raise some success counts without moving the boundary;
3. neither intervention alone expands the tested 50% reachable region beyond lambda `0.80`.

A next bounded software test should distinguish **action discretization / controller class** from a deeper **global-control reachability limit**. One clean option is preregistered model-predictive or bounded continuous-condition planning over the same transition surrogate, compared against the frozen expanded tabular policy.

## Important limitations

- The expanded action set is hand-designed and small.
- Training budget remains fixed at 2400 episodes despite the larger action vocabulary.
- Q-learning remains tabular.
- All actions remain global; there is no spatially localized actuation.
- The transition model is synthetic and dimensionless.
- Declared control effort is not physical energy.
- Failure to move lambda50 rejects only this preregistered action-space test, not all possible action representations.

## Non-claims

Experiment 009 does not establish physical programmable matter, a real material phase boundary, physical self-repair, physical energy savings, or general AI superiority.