"""MorphoMatter Experiment 019: orientation kinetics and finite-rate path memory."""
from __future__ import annotations

from collections import defaultdict
from statistics import mean

from morphomatter.interface_chemistry import external_interface_c1
from morphomatter.nucleation import NucleationConfig
from morphomatter.orientation_kinetics import (
    MATCHED_PAIRS,
    SEEDS,
    run_fast_cycle,
    run_slow_anneal,
    static_controls_hold,
    validate_protocol,
)
from morphomatter.particle_environment import particle_environment_metrics

SHARED_BETAS = (0.5, 1.0, 2.0, 4.0)
HARD_CONFIG = NucleationConfig(
    width=9, height=9, seed=0,
    spontaneous_rate=0.002,
    nucleation_drive_gain=0.18,
    frontier_base=0.03,
    frontier_neighbor_gain=0.50,
    frontier_drive_gain=0.12,
    commit_base=0.14,
    commit_neighbor_gain=0.30,
    commit_drive_gain=0.25,
    barrier=0.16,
)


def main() -> None:
    validate_protocol()
    if not static_controls_hold():
        raise RuntimeError("Experiment 018 static controls drifted")
    background = particle_environment_metrics(1.0, 1.0)
    if background.regime != "REVERSIBLE_ASSEMBLY":
        raise RuntimeError("Experiment 017 background drifted")
    interface_c1 = external_interface_c1(HARD_CONFIG, 180.0)
    if abs(interface_c1 - 0.700000000) > 1e-12:
        raise RuntimeError("Experiment 015 interface control drifted")

    reachability_passes = 0
    reachability_counts: dict[str, int] = {}
    path_passes = 0
    reversibility_passes = 0

    print("orientation_kinetics_reachability: particle motif successes mean_final_quality")
    for particle, motif in MATCHED_PAIRS:
        slow = tuple(run_slow_anneal(particle, motif, seed) for seed in SEEDS)
        successes = sum(int(row.success) for row in slow)
        mean_quality = mean(row.final_metrics.quality for row in slow)
        reachability_counts[particle] = successes
        reachability_passes += int(successes >= 24)
        print(
            f"particle={particle} motif={motif} successes={successes}/32 "
            f"mean_final_quality={mean_quality:.9f}"
        )

    print("orientation_kinetics_cycle: particle H0.5 H1 H2 H4 H_area positive_points Q_initial Q_relaxed delta_relaxed")
    for particle, motif in MATCHED_PAIRS:
        cycles = tuple(run_fast_cycle(particle, motif, seed) for seed in SEEDS)
        forward: dict[float, list[float]] = defaultdict(list)
        reverse: dict[float, list[float]] = defaultdict(list)
        for row in cycles:
            for beta, q in row.forward_quality:
                forward[float(beta)].append(float(q))
            for beta, q in row.reverse_quality:
                reverse[float(beta)].append(float(q))

        h = {beta: mean(reverse[beta]) - mean(forward[beta]) for beta in SHARED_BETAS}
        h_area = mean(h.values())
        positive_points = sum(int(h[beta] > 0.0) for beta in SHARED_BETAS)
        path_signal = h_area >= 0.05 and positive_points >= 3
        path_passes += int(path_signal)

        initial_mean = mean(row.initial_quality for row in cycles)
        relaxed_mean = mean(row.relaxed_quality for row in cycles)
        relaxed_delta = abs(relaxed_mean - initial_mean)
        reversible = relaxed_delta <= 0.08
        reversibility_passes += int(reversible)

        print(
            f"particle={particle} H0.5={h[0.5]:.9f} H1={h[1.0]:.9f} "
            f"H2={h[2.0]:.9f} H4={h[4.0]:.9f} H_area={h_area:.9f} "
            f"positive_points={positive_points} Q_initial={initial_mean:.9f} "
            f"Q_relaxed={relaxed_mean:.9f} delta_relaxed={relaxed_delta:.9f} "
            f"path_signal={path_signal} reversible={reversible}"
        )

    no_pair_below_16 = all(value >= 16 for value in reachability_counts.values())
    reachability_ok = reachability_passes >= 3 and no_pair_below_16
    path_memory_ok = path_passes >= 2
    reversibility_ok = reversibility_passes >= 3

    if reachability_ok and path_memory_ok and reversibility_ok:
        label = "ORIENTATION_KINETICS_REACHABLE_WITH_PATH_MEMORY"
    elif reachability_ok and reversibility_ok and not path_memory_ok:
        label = "ORIENTATION_KINETICS_REACHABLE_NO_PATH_MEMORY"
    elif path_memory_ok and not reachability_ok:
        label = "ORIENTATION_KINETICS_PATH_MEMORY_WITH_LIMITED_REACHABILITY"
    else:
        label = "ORIENTATION_KINETICS_MIXED_OR_NEGATIVE"

    print(
        f"reachability_passes={reachability_passes}/4 "
        f"no_pair_below_16={no_pair_below_16} reachability_ok={reachability_ok}"
    )
    print(f"path_memory_passes={path_passes}/4 path_memory_ok={path_memory_ok}")
    print(f"reversibility_passes={reversibility_passes}/4 reversibility_ok={reversibility_ok}")
    print(f"background_regime={background.regime} interface_control={interface_c1:.9f}")
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
