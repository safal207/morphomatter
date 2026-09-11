"""MorphoMatter Experiment 002: nucleation -> frontier -> mostly ordered state.

This is a pinned dimensionless toy experiment, not a physical crystallization
result. It demonstrates a two-stage global condition schedule: first make rare
nuclei possible, then lower direct drive while strengthening local coupling so
an ordering frontier can propagate.
"""
from collections import Counter

from morphomatter import Conditions
from morphomatter.nucleation import NucleationConfig, NucleationLattice


NUCLEATION_CONDITIONS = Conditions(
    drive=0.45,
    coupling_scale=1.0,
    threshold_scale=0.8,
)
PROPAGATION_CONDITIONS = Conditions(
    drive=0.12,
    coupling_scale=1.5,
    threshold_scale=0.8,
)
CHECKPOINTS = {1, 2, 4, 8, 12, 18, 24}


def counts(model: NucleationLattice) -> tuple[int, int, int]:
    disordered = sum(phase.value == 0 for phase in model.state)
    metastable = sum(phase.value == 1 for phase in model.state)
    ordered = sum(phase.value == 2 for phase in model.state)
    return disordered, metastable, ordered


def main() -> None:
    model = NucleationLattice(config=NucleationConfig(width=9, height=9, seed=26))
    mechanisms: Counter[str] = Counter()

    for tick in range(1, 25):
        conditions = NUCLEATION_CONDITIONS if tick <= 2 else PROPAGATION_CONDITIONS
        events = model.step(conditions)
        mechanisms.update(event.mechanism for event in events)

        if tick in CHECKPOINTS:
            disordered, metastable, ordered = counts(model)
            print(
                f"tick={tick:02d} D={disordered:02d} M={metastable:02d} "
                f"O={ordered:02d} frontier={len(model.frontier_sites()):02d}"
            )
            for row in model.rows():
                print(row)
            print()

    print("mechanisms:", dict(sorted(mechanisms.items())))
    print(f"ordered_fraction={model.ordered_fraction():.6f}")
    print(f"replay_verified={model.replay() == tuple(model.state)}")

    required = {"nucleation", "frontier_growth", "commit"}
    if not required.issubset(mechanisms):
        raise SystemExit(f"missing mechanisms: {sorted(required - set(mechanisms))}")
    if model.ordered_fraction() < 0.90:
        raise SystemExit("reference trajectory did not reach >= 90% ordered")
    if model.replay() != tuple(model.state):
        raise SystemExit("transition replay mismatch")


if __name__ == "__main__":
    main()
