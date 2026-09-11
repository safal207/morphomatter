import unittest

from morphomatter.generalization import (
    EvaluationRun,
    paired_median_advantage_interval,
    percentile_bootstrap_interval,
    summarize_runs,
    wilson_interval,
)


class GeneralizationStatisticsTests(unittest.TestCase):
    def test_wilson_interval_contains_observed_rate(self):
        low, high = wilson_interval(58, 64)
        observed = 58 / 64
        self.assertLess(low, observed)
        self.assertGreater(high, observed)
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)

    def test_bootstrap_is_deterministic_for_fixed_seed(self):
        values = (0.4, 0.6, 0.8, 1.0, 1.2)
        left = percentile_bootstrap_interval(values, seed=5005, resamples=200)
        right = percentile_bootstrap_interval(values, seed=5005, resamples=200)
        self.assertEqual(left, right)

    def test_paired_advantage_uses_joint_successes_only(self):
        learned = (
            EvaluationRun(True, 1.0, 4, True),
            EvaluationRun(False, None, None, True),
            EvaluationRun(True, 1.5, 5, True),
        )
        cooperative = (
            EvaluationRun(True, 2.0, 5, True),
            EvaluationRun(True, 2.5, 6, True),
            EvaluationRun(True, 2.0, 6, True),
        )
        value, interval, count = paired_median_advantage_interval(
            learned, cooperative, seed=12, resamples=200
        )
        self.assertEqual(count, 2)
        self.assertGreater(value, 0.0)
        self.assertGreater(interval[0], 0.0)

    def test_summary_reports_replay_failures(self):
        runs = (
            EvaluationRun(True, 1.0, 3, True),
            EvaluationRun(True, 2.0, 4, False),
            EvaluationRun(False, None, None, True),
        )
        summary = summarize_runs(runs, bootstrap_seed=10, resamples=100)
        self.assertEqual(summary.successes, 2)
        self.assertEqual(summary.replay_failures, 1)
        self.assertAlmostEqual(summary.success_rate, 2 / 3)


if __name__ == "__main__":
    unittest.main()
