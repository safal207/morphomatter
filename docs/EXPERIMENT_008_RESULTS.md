# Experiment 008 — rich-state causality test results

## Provenance

Preregistration was committed before the first Experiment 008 result:

`b6c84893dc7ad94c29f8ff89a94753fee5c7dbe4`

The first completed preregistered Experiment 008 CI run executed on branch implementation head:

`f1479873b8d8b43ce399f3eb80be36ca457191d8`

GitHub Actions PR run: `34565936117`.

The run passed `28` unit tests and Experiments 002–008. The Experiment 007 coarse/cooperative/brute/random success counts reproduced exactly at every lambda before the rich-state comparison was interpreted.

## Frozen result

Preregistered label:

`RICH_STATE_EFFORT_ONLY`

The rich observation did **not** shift the 50% controllability boundary.

| Controller | lambda50 |
|---|---:|
| rich learned | `0.80` |
| coarse learned | `0.80` |
| cooperative heuristic | `0.80` |
| random | `0.60` |
| brute-force | `NONE` |

There was no preregistered separation point at which rich success was at least 50% while both coarse and cooperative success were below 50%.

## Success curve and learned effort

| lambda | Rich success | Rich median effort | Coarse success | Coarse median effort | Cooperative success | Cooperative median effort |
|---:|---:|---:|---:|---:|---:|---:|
| `0.00` | `49/64` (`76.6%`) | `1.140` | `49/64` (`76.6%`) | `0.750` | `57/64` (`89.1%`) | `1.900` |
| `0.20` | `45/64` (`70.3%`) | `1.520` | `46/64` (`71.9%`) | `0.840` | `49/64` (`76.6%`) | `1.900` |
| `0.40` | `42/64` (`65.6%`) | `1.520` | `42/64` (`65.6%`) | `1.420` | `42/64` (`65.6%`) | `2.090` |
| `0.60` | `39/64` (`60.9%`) | `1.520` | `38/64` (`59.4%`) | `1.610` | `38/64` (`59.4%`) | `2.090` |
| `0.80` | `32/64` (`50.0%`) | **`1.470`** | `32/64` (`50.0%`) | `1.795` | `33/64` (`51.6%`) | `2.280` |
| `1.00` | `16/64` (`25.0%`) | **`1.710`** | `16/64` (`25.0%`) | `2.035` | `16/64` (`25.0%`) | `2.280` |

All rich-policy replay failures: `0`.

## Interpretation

Experiment 008 changes only the policy observation while preserving the Experiment 007 transition law, lambda grid, action set, reward, training budget, damage geometries, training/held-out seeds, recovery goal, and horizon.

The richer observation includes the coarse global state plus connected-defect geometry, component count, frontier support, recent commit progress, and remaining horizon. It does not receive held-out geometry names, seed identifiers, future stochastic draws, or target-case identities.

The result does **not** support the hypothesis that these additional state features expand the current controllability boundary. `lambda50` remains `0.80`, identical to both the coarse learner and fixed cooperative heuristic.

The result does support the preregistered secondary interpretation at the shared boundary: at lambda `0.80`, rich control reaches the same `32/64` success count as the coarse learner while reducing median declared effort from `1.795` to `1.470`; it is also below the cooperative heuristic's `2.280`. The same qualitative effort reduction remains visible at lambda `1.00` among successful runs.

This suggests that the Experiment 007 capability ceiling is not explained solely by missing coarse geometric/history information. In this toy model, richer observation improves condition-selection efficiency near the boundary but does not create access to states beyond the existing cooperative-control boundary.

## Important limitations

- The state representation is hand-engineered and discretized.
- Q-learning is tabular and deliberately small.
- The action set remains only five global condition settings.
- The transition model is dimensionless and synthetic.
- Median control effort is an algorithmic score, not physical energy.
- Equal `lambda50` does not prove that all richer observations are useless; it rejects only this preregistered encoder/controller test.

## Non-claims

Experiment 008 does not establish physical programmable matter, physical self-repair, a real material phase boundary, physical energy savings, or general AI superiority.
