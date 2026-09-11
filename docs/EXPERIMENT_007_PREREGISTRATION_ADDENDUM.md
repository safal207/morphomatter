# Experiment 007 preregistration addendum — undefined boundary semantics

Status: **FROZEN BEFORE FIRST BOUNDARY-MATRIX EXECUTION**

The main preregistration defines `lambda50 = NONE` when a strategy never reaches 50% success on the tested lambda grid but does not explicitly define arithmetic comparisons against `NONE`.

For the frozen Experiment 007 interpretation only:

- if learned `lambda50 = NONE`, `CONTROLLABILITY_BOUNDARY_SHIFT_SIGNAL` is impossible;
- if learned has a numeric `lambda50` and a comparator has `lambda50 = NONE`, the learned boundary is treated as being at least one full grid step (`0.20`) above that comparator for criteria 3 or 4;
- if both boundaries are numeric, use ordinary subtraction on the tested grid;
- no synthetic numeric lambda is assigned to `NONE` and no interpolation outside the tested grid is permitted.

This clarification changes no endpoint, lambda value, seed, geometry, learner setting, comparator, metric, or success threshold.