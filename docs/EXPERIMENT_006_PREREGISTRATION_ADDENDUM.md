# Experiment 006 — preregistration addendum

Status: **FROZEN BEFORE FIRST HARD-REGIME MATRIX EXECUTION**

This addendum supplies deterministic seeds that were omitted from the original Experiment 006 preregistration. It does not change the hard law, training surface, held-out matrix, comparators, endpoint, thresholds, or interpretation labels.

## Frozen deterministic analysis seeds

Use 2000 bootstrap resamples throughout.

- learned summary bootstrap seed: `6007`;
- cooperative summary bootstrap seed: `6008`;
- brute-force summary bootstrap seed: `6009`;
- pooled-random summary bootstrap seed: `6010`;
- paired cooperative-minus-learned effort bootstrap seed: `6011`.

## Frozen random schedule generation

For held-out case index `i` in deterministic geometry-major / seed-minor order and replicate index `r` in `0..15`, generate the seven-action random schedule with Python `random.Random(606000 + i * 100 + r)` and uniform draws from the existing `RECOVERY_ACTIONS` key order.

The recovery material seed remains the held-out case seed and is not changed by the random-schedule RNG.

## Frozen implementation note

When cloning the hard `NucleationConfig` for a case, only the `seed` field may change. All other hard-law fields must exactly match the original Experiment 006 preregistration.
