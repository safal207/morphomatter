"""Print a small dimensionless MorphoMatter transition map and one schedule.

Run from the repository root:
    PYTHONPATH=src python experiments/transition_map.py
"""
from morphomatter import ModelConfig, Phase, TransitionLattice
from morphomatter.explorer import TransitionMapExplorer, condition_grid


def seeded_initial(width: int, height: int) -> tuple[Phase, ...]:
    state = [Phase.DISORDERED] * (width * height)
    center = (height // 2) * width + (width // 2)
    state[center] = Phase.ORDERED
    return tuple(state)


def main() -> None:
    config = ModelConfig(
        width=5,
        height=5,
        transition_threshold=0.55,
        metastable_threshold=0.15,
        neighbor_coupling=0.45,
        memory_decay=0.0,
    )
    initial = seeded_initial(config.width, config.height)
    space = condition_grid(
        drives=(-0.2, 0.0, 0.2, 0.4, 0.6),
        coupling_scales=(0.5, 1.0, 1.5),
        threshold_scales=(0.75, 1.0, 1.25),
    )
    explorer = TransitionMapExplorer(config, steps_per_point=3)
    records = explorer.scan(initial, space)

    print("drive,coupling_scale,threshold_scale,dominant_phase,score,ordered_fraction,transitions")
    for record in records:
        c = record.conditions
        print(
            f"{c.drive:.3f},{c.coupling_scale:.3f},{c.threshold_scale:.3f},"
            f"{record.dominant_phase.name},{record.organization_score:.6f},"
            f"{record.ordered_fraction:.6f},{record.transition_count}"
        )

    search_space = condition_grid(
        drives=(0.0, 0.2, 0.4, 0.6),
        coupling_scales=(0.5, 1.0, 1.5),
        threshold_scales=(0.75, 1.0),
    )
    result = explorer.find_schedule(
        initial,
        search_space,
        goal_score=0.90,
        max_steps=4,
    )

    print("\nlow-cost schedule to score >= 0.90")
    if result is None:
        print("NO_SCHEDULE_FOUND")
        return

    model = TransitionLattice(initial, config=config)
    for index, conditions in enumerate(result.schedule, start=1):
        model.step(conditions)
        print(
            f"{index}: drive={conditions.drive:.3f} "
            f"coupling={conditions.coupling_scale:.3f} "
            f"threshold={conditions.threshold_scale:.3f} "
            f"score={model.organization_score():.6f}"
        )
    print(f"declared_cost={result.cost:.6f}")
    print(f"replay_ok={model.replay() == tuple(model.state)}")


if __name__ == "__main__":
    main()
