"""MorphoMatter Experiment 018: directional particle topology × structure."""
from __future__ import annotations

from collections import defaultdict

from morphomatter.environment_screening import interaction_metrics
from morphomatter.interface_chemistry import external_interface_c1
from morphomatter.nucleation import NucleationConfig
from morphomatter.particle_anisotropy import (
    CONTACT_MOTIFS,
    DIRECTIONAL_BUDGET,
    PARTICLE_TOPOLOGIES,
    StructuralOptimum,
    full_matrix,
    preferred_motif,
    validate_frozen_protocol,
)

BACKGROUND_Q_REL = 1.00
BACKGROUND_I = 1.00
EXPECTED_BACKGROUND_REGIME = "REVERSIBLE_ASSEMBLY"
EXPECTED_INTERFACE_C1 = 0.700000000

HARD_CONFIG = NucleationConfig(
    width=9,
    height=9,
    seed=0,
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

MATCHED = {
    "axial2": "axial_ring6",
    "corner2": "corner_loop4",
    "tri3": "tri_ladder8",
    "isotropic4": "square_torus9",
}


def _fmt_orientations(values: tuple[int, ...]) -> str:
    return "[" + ",".join(str(value * 90) for value in values) + "]"


def _ranking(rows: tuple[StructuralOptimum, ...]) -> tuple[str, ...]:
    ordered = sorted(
        rows,
        key=lambda row: (
            -row.edge_coverage,
            -row.budget_utilization,
            row.motif,
        ),
    )
    return tuple(row.motif for row in ordered)


def _ranking_inversions(a: tuple[StructuralOptimum, ...], b: tuple[StructuralOptimum, ...]) -> int:
    by_name_a = {row.motif: row for row in a}
    by_name_b = {row.motif: row for row in b}
    names = tuple(sorted(by_name_a))
    inversions = 0
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            score_a_l = by_name_a[left].score_pair
            score_a_r = by_name_a[right].score_pair
            score_b_l = by_name_b[left].score_pair
            score_b_r = by_name_b[right].score_pair
            sign_a = (score_a_l > score_a_r) - (score_a_l < score_a_r)
            sign_b = (score_b_l > score_b_r) - (score_b_l < score_b_r)
            if sign_a != 0 and sign_b != 0 and sign_a != sign_b:
                inversions += 1
    return inversions


def main() -> None:
    validate_frozen_protocol()

    background = interaction_metrics(BACKGROUND_I)
    interface_c1 = external_interface_c1(HARD_CONFIG, 180.0)

    if abs(BACKGROUND_Q_REL - 1.0) > 1e-12 or abs(BACKGROUND_I - 1.0) > 1e-12:
        raise SystemExit("preregistered background coordinates drifted")
    if background.regime != EXPECTED_BACKGROUND_REGIME:
        raise SystemExit(
            f"Experiment 016/017 background drifted: {background.regime}"
        )
    if abs(interface_c1 - EXPECTED_INTERFACE_C1) > 1e-12:
        raise SystemExit(f"Experiment 015 interface control drifted: {interface_c1}")

    rows = full_matrix()
    if len(rows) != 16:
        raise SystemExit(f"preregistered matrix size changed: {len(rows)}")

    print(
        "particle_anisotropy_matrix: particle motif coverage utilization "
        "bond_strength optimum_count assignments canonical_orientations"
    )
    for row in rows:
        print(
            f"particle={row.particle} motif={row.motif} "
            f"coverage={row.edge_coverage:.9f} "
            f"utilization={row.budget_utilization:.9f} "
            f"bond_strength={row.total_bond_strength:.9f} "
            f"optimum_count={row.optimal_assignment_count} "
            f"assignments={row.assignments_evaluated} "
            f"canonical={_fmt_orientations(row.canonical_orientations)}"
        )

    grouped: dict[str, list[StructuralOptimum]] = defaultdict(list)
    for row in rows:
        grouped[row.particle].append(row)

    unique_preferences: dict[str, str] = {}
    preference_scores: dict[str, tuple[float, float]] = {}
    rankings: dict[str, tuple[str, ...]] = {}

    print("particle_preferences: particle preferred unique coverage utilization ranking")
    for topology in PARTICLE_TOPOLOGIES:
        particle_rows = tuple(grouped[topology.name])
        preferred, unique, score = preferred_motif(particle_rows)
        rankings[topology.name] = _ranking(particle_rows)
        if unique:
            unique_preferences[topology.name] = preferred
        preference_scores[topology.name] = score
        print(
            f"particle={topology.name} preferred={preferred} unique={unique} "
            f"coverage={score[0]:.9f} utilization={score[1]:.9f} "
            f"ranking={rankings[topology.name]}"
        )

    matched_perfect = 0
    print("matched_pairs: particle motif coverage utilization perfect")
    by_cell = {(row.particle, row.motif): row for row in rows}
    for particle, motif in MATCHED.items():
        row = by_cell[(particle, motif)]
        perfect = (
            abs(row.edge_coverage - 1.0) <= 1e-12
            and abs(row.budget_utilization - 1.0) <= 1e-12
        )
        matched_perfect += int(perfect)
        print(
            f"particle={particle} motif={motif} "
            f"coverage={row.edge_coverage:.9f} "
            f"utilization={row.budget_utilization:.9f} perfect={perfect}"
        )

    topology_names = tuple(item.name for item in PARTICLE_TOPOLOGIES)
    ranking_pairs = []
    total_inversions = 0
    identical_rankings = []
    for i, left in enumerate(topology_names):
        for right in topology_names[i + 1 :]:
            inversions = _ranking_inversions(
                tuple(grouped[left]), tuple(grouped[right])
            )
            total_inversions += inversions
            identical = rankings[left] == rankings[right]
            if identical:
                identical_rankings.append((left, right))
            ranking_pairs.append((left, right, inversions, identical))

    for left, right, inversions, identical in ranking_pairs:
        print(
            f"ranking_pair left={left} right={right} "
            f"inversions={inversions} identical={identical}"
        )

    unique_count = len(unique_preferences)
    distinct_unique_motifs = len(set(unique_preferences.values()))
    budgets_equal = all(abs(item.budget - DIRECTIONAL_BUDGET) <= 1e-12 for item in PARTICLE_TOPOLOGIES)

    positive = (
        len(rows) == 16
        and budgets_equal
        and unique_count >= 3
        and distinct_unique_motifs >= 3
        and matched_perfect >= 3
        and background.regime == EXPECTED_BACKGROUND_REGIME
        and abs(interface_c1 - EXPECTED_INTERFACE_C1) <= 1e-12
    )

    label = (
        "DIRECTIONAL_TOPOLOGY_SELECTS_STRUCTURE"
        if positive
        else "DIRECTIONAL_TOPOLOGY_STRUCTURE_SELECTIVITY_MIXED"
    )

    print(f"directional_budget={DIRECTIONAL_BUDGET:.9f} budgets_equal={budgets_equal}")
    print(
        f"background q_rel={BACKGROUND_Q_REL:.2f} I={BACKGROUND_I:.2f} "
        f"regime={background.regime} IC_C1_control={interface_c1:.9f}"
    )
    print(
        f"unique_preferences={unique_count}/4 "
        f"distinct_unique_motifs={distinct_unique_motifs} "
        f"matched_perfect={matched_perfect}/4"
    )
    print(f"unique_preference_map={unique_preferences}")
    print(f"total_pairwise_ranking_inversions={total_inversions}")
    print(f"identical_ranking_pairs={tuple(identical_rankings)}")
    print(f"PREREGISTERED_RESULT={label}")


if __name__ == "__main__":
    main()
