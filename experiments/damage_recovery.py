"""MorphoMatter Experiment 003: damage -> renucleation -> recovery.

This is a pinned dimensionless comparison, not a physical self-healing result.
All recovery strategies start from the same damaged state and use the same
recovery seed so the stochastic surface is held fixed.
"""
from morphomatter import Conditions
from morphomatter.nucleation import NucleationConfig, NucleationLattice
from morphomatter.recovery import apply_damage, compare_recovery_strategies, rectangular_sites


ASSEMBLY = (
    [Conditions(drive=0.45, coupling_scale=1.0, threshold_scale=0.8)] * 2
    + [Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)] * 22
)

RENucleation = Conditions(drive=0.55, coupling_scale=1.0, threshold_scale=0.8)
COOPERATIVE_PROPAGATION = Conditions(drive=0.12, coupling_scale=1.5, threshold_scale=0.8)
NO_COUPLING_PROPAGATION = Conditions(drive=0.12, coupling_scale=0.0, threshold_scale=0.8)
BRUTE_FORCE = Conditions(drive=0.80, coupling_scale=0.0, threshold_scale=0.8)


def build_reference_state() -> tuple:
    model = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
    model.run(ASSEMBLY)
    if abs(model.ordered_fraction() - (77 / 81)) > 1e-12:
        raise SystemExit("Experiment 002 reference state changed")
    return tuple(model.state)


def main() -> None:
    reference = build_reference_state()
    damage_sites = rectangular_sites(
        width=9,
        height=9,
        top=2,
        left=2,
        rows=4,
        cols=5,
    )
    damage = apply_damage(reference, damage_sites)

    cooperative = [RENucleation] * 2 + [COOPERATIVE_PROPAGATION] * 10
    no_coupling = [RENucleation] * 2 + [NO_COUPLING_PROPAGATION] * 10
    brute_force = [BRUTE_FORCE] * 12

    results = compare_recovery_strategies(
        damage.after,
        config=NucleationConfig(width=9, height=9, seed=11),
        strategies={
            "cooperative_coupling": cooperative,
            "no_coupling": no_coupling,
            "brute_force_high_drive": brute_force,
        },
        goal_fraction=0.90,
    )

    print(
        f"reference_ordered={sum(p.value == 2 for p in reference)}/81 "
        f"damaged_ordered={sum(p.value == 2 for p in damage.after)}/81 "
        f"ordered_sites_removed={damage.ordered_sites_removed}"
    )
    for result in results:
        print(
            f"{result.name}: final={result.final_ordered_fraction:.6f} "
            f"goal_tick={result.first_goal_tick} "
            f"effort={result.control_effort:.3f} "
            f"gain_per_effort={result.gain_per_effort:.6f} "
            f"mechanisms={dict(result.mechanism_counts)} "
            f"replay={result.replay_verified}"
        )

    by_name = {result.name: result for result in results}
    cooperative_result = by_name["cooperative_coupling"]
    no_coupling_result = by_name["no_coupling"]
    brute_result = by_name["brute_force_high_drive"]

    if damage.ordered_sites_removed != 20:
        raise SystemExit("pinned damage intervention changed")
    if cooperative_result.final_ordered_fraction < 0.99:
        raise SystemExit("cooperative recovery did not restore near-complete order")
    if cooperative_result.first_goal_tick is None or cooperative_result.first_goal_tick > 6:
        raise SystemExit("cooperative recovery crossed 90% too late")
    if cooperative_result.final_ordered_fraction <= no_coupling_result.final_ordered_fraction:
        raise SystemExit("coupling did not improve final recovery over no-coupling control")
    if cooperative_result.gain_per_effort <= brute_result.gain_per_effort:
        raise SystemExit("cooperative recovery did not beat brute-force gain per effort")
    if not all(result.replay_verified for result in results):
        raise SystemExit("one or more recovery traces failed replay")


if __name__ == "__main__":
    main()
