"""MorphoMatter Experiment 020: translational self-assembly with directional particles."""
from __future__ import annotations

from statistics import median

from morphomatter.particle_anisotropy import PARTICLE_TOPOLOGIES
from morphomatter.translational_assembly import (
    BETA_SCHEDULE,
    PARTICLE_COUNT,
    SEEDS,
    SWEEPS_PER_BETA,
    background_controls_hold,
    run_anneal,
    validate_protocol,
)


def _med(values: list[float]) -> float:
    return float(median(values))


def main() -> None:
    validate_protocol()
    topology_names = tuple(item.name for item in PARTICLE_TOPOLOGIES)
    if topology_names != ("isotropic4", "axial2", "corner2", "tri3"):
        raise SystemExit("preregistered topology set changed")
    if SEEDS != tuple(range(20001, 20033)):
        raise SystemExit("preregistered seed set changed")
    if BETA_SCHEDULE != (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
        raise SystemExit("preregistered beta schedule changed")
    if SWEEPS_PER_BETA != 300 or PARTICLE_COUNT != 8:
        raise SystemExit("preregistered kinetic protocol changed")

    summaries: dict[str, dict[str, float]] = {}
    replay_failures = 0
    control_failures = 0

    print(
        "translational_summary: particle beta0_util final_util delta_util "
        "largest_component mean_degree axial corner branch cross accepted_fraction"
    )

    for particle_name in topology_names:
        rows = []
        for seed in SEEDS:
            result = run_anneal(particle_name, seed)
            replay = run_anneal(particle_name, seed)
            if result != replay:
                replay_failures += 1
            rows.append(result)

        beta0_util = _med([row.beta0_metrics.binding_utilization for row in rows])
        final_util = _med([row.final_metrics.binding_utilization for row in rows])
        delta_util = _med([row.delta_utilization for row in rows])
        largest_component = _med([row.final_metrics.largest_component_fraction for row in rows])
        mean_degree = _med([row.final_metrics.mean_active_degree for row in rows])
        axial = _med([row.final_metrics.axial_fraction for row in rows])
        corner = _med([row.final_metrics.corner_fraction for row in rows])
        branch = _med([row.final_metrics.branch_fraction for row in rows])
        cross = _med([row.final_metrics.cross_fraction for row in rows])
        accepted_fraction = _med([row.accepted / row.proposals for row in rows])

        summaries[particle_name] = {
            "beta0_util": beta0_util,
            "final_util": final_util,
            "delta_util": delta_util,
            "largest_component": largest_component,
            "mean_degree": mean_degree,
            "axial": axial,
            "corner": corner,
            "branch": branch,
            "cross": cross,
            "accepted_fraction": accepted_fraction,
        }

        print(
            f"particle={particle_name} beta0_util={beta0_util:.9f} "
            f"final_util={final_util:.9f} delta_util={delta_util:.9f} "
            f"largest_component={largest_component:.9f} mean_degree={mean_degree:.9f} "
            f"axial={axial:.9f} corner={corner:.9f} branch={branch:.9f} cross={cross:.9f} "
            f"accepted_fraction={accepted_fraction:.9f}"
        )

        # Median assembly trajectory by beta, useful evidence but not a separate
        # primary criterion.
        for stage_index, beta in enumerate(BETA_SCHEDULE):
            util = _med([
                row.stage_metrics[stage_index][1].binding_utilization
                for row in rows
            ])
            component = _med([
                row.stage_metrics[stage_index][1].largest_component_fraction
                for row in rows
            ])
            print(
                f"stage particle={particle_name} beta={beta:.1f} "
                f"median_util={util:.9f} median_component={component:.9f}"
            )

    axial_signature = (
        summaries["axial2"]["axial"]
        >= summaries["axial2"]["corner"] + 0.10 - 1e-12
    )
    corner_signature = (
        summaries["corner2"]["corner"]
        >= summaries["corner2"]["axial"] + 0.10 - 1e-12
    )
    tri_signature = (
        summaries["tri3"]["branch"]
        >= summaries["axial2"]["branch"] + 0.10 - 1e-12
        and summaries["tri3"]["branch"]
        >= summaries["corner2"]["branch"] + 0.10 - 1e-12
    )
    isotropic_signature = (
        summaries["isotropic4"]["mean_degree"]
        >= summaries["axial2"]["mean_degree"] + 0.25 - 1e-12
        and summaries["isotropic4"]["mean_degree"]
        >= summaries["corner2"]["mean_degree"] + 0.25 - 1e-12
    )

    signature_map = {
        "isotropic4": isotropic_signature,
        "axial2": axial_signature,
        "corner2": corner_signature,
        "tri3": tri_signature,
    }
    signature_passes = sum(int(value) for value in signature_map.values())

    assembly_map = {
        name: values["delta_util"] >= 0.10 - 1e-12
        for name, values in summaries.items()
    }
    connectivity_map = {
        name: values["largest_component"] >= 0.50 - 1e-12
        for name, values in summaries.items()
    }
    assembly_passes = sum(int(value) for value in assembly_map.values())
    connectivity_passes = sum(int(value) for value in connectivity_map.values())

    if not background_controls_hold():
        control_failures += 1

    label = (
        "TRANSLATIONAL_DYNAMICS_PRESERVE_DIRECTIONAL_SELECTION"
        if signature_passes >= 3
        and assembly_passes >= 3
        and connectivity_passes >= 3
        and control_failures == 0
        and replay_failures == 0
        else "TRANSLATIONAL_SELECTION_MIXED_OR_NEGATIVE"
    )

    print(f"signature_map={signature_map} signature_passes={signature_passes}/4")
    print(f"assembly_map={assembly_map} assembly_passes={assembly_passes}/4")
    print(f"connectivity_map={connectivity_map} connectivity_passes={connectivity_passes}/4")
    print(f"replay_failures={replay_failures}")
    print(f"control_failures={control_failures}")
    print(f"primary_trajectories={len(topology_names) * len(SEEDS)}")
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
