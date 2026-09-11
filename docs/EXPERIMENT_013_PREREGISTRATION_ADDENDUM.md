# Experiment 013 preregistration addendum — numerical bound semantics

This addendum is committed **before the first Experiment 013 result**.

The original preregistration freezes finite numerical search bounds:

- drive `[0, 20]`;
- coupling `[0, 30]`.

Clarification: if an analytic aggregate root is finite but strictly above the corresponding frozen numerical upper bound, and the actual-law bisection precheck confirms that the 50% target is not reached at that upper bound, numerical `NONE` is considered **consistent outside the measurement range**.

Likewise, analytic `+inf` paired with numerical `NONE` remains consistent.

A finite analytic root inside the numerical search interval must still be recovered to the frozen `1e-6` absolute tolerance.

This clarification changes no masks, PDE boundary conditions, material parameters, target fraction, lambda grid, control envelope, effect threshold, or primary result rule.
