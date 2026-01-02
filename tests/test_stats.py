import unittest
import numpy as np
from whatts.stats import (
    hazen_interpolate,
    inverse_hazen,
    score_test_probability,
    wilson_score_upper_tolerance,
    calculate_neff_sum_corr
)

class TestStats(unittest.TestCase):
    def test_hazen_interpolate_and_inverse(self):
        # Data: 1 to 10
        data = np.arange(1, 11, dtype=float)

        # Test interpolation
        # Rank 0.05 -> Value 1.0
        self.assertAlmostEqual(hazen_interpolate(data, 0.05), 1.0)
        # Rank 0.95 -> Value 10.0
        self.assertAlmostEqual(hazen_interpolate(data, 0.95), 10.0)

        # Test inverse
        # Value 1.0 -> Rank 0.05
        self.assertAlmostEqual(inverse_hazen(data, 1.0), 0.05)
        # Value 10.0 -> Rank 0.95
        self.assertAlmostEqual(inverse_hazen(data, 10.0), 0.95)

        # Test clamping
        # Should now return 0.0 and 1.0 exactly
        self.assertEqual(inverse_hazen(data, -100), 0.0)
        self.assertEqual(inverse_hazen(data, 100), 1.0)

    def test_wilson_score_upper_tolerance(self):
        # Validation Case: n=30, p=0.95, alpha=0.05 (conf=0.95)
        n = 30
        p_hat = 0.95

        utl_rank = wilson_score_upper_tolerance(p_hat, n, n_eff=30, conf_level=0.95)

        self.assertTrue(p_hat < utl_rank <= 1.0)

        # Test with low n_eff
        utl_rank_low_neff = wilson_score_upper_tolerance(p_hat, n, n_eff=5, conf_level=0.95)
        # Lower n_eff should result in wider interval (higher UTL rank)
        # unless it hits 1.0.
        # With n_eff=5, p=0.95, it likely hits 1.0.
        # utl_rank might be 0.99.
        # Let's check >= instead of > to be safe if both are 1.0
        self.assertTrue(utl_rank_low_neff >= utl_rank)

    def test_score_test_probability(self):
        # If obs rank == null percentile, prob should be 0.5
        prob = score_test_probability(0.95, 0.95, n_eff=30)
        self.assertAlmostEqual(prob, 0.5)

        prob_high = score_test_probability(0.99, 0.95, n_eff=30)
        self.assertTrue(prob_high > 0.5)

        # If Limit is low (rank 0.5), we are NOT confident.
        prob_low = score_test_probability(0.50, 0.95, n_eff=30)
        self.assertTrue(prob_low < 0.01)

    def test_calculate_neff(self):
        # Independent data (white noise)
        np.random.seed(42)
        data = np.random.normal(0, 1, 100)
        n_eff = calculate_neff_sum_corr(data)
        # Should be close to n=100
        self.assertTrue(n_eff > 50)

        # Highly correlated data (constant)
        data_const = np.ones(100)
        # FIX: Constant data implies 1 effective sample repeated N times.
        self.assertEqual(calculate_neff_sum_corr(data_const), 1.0)

if __name__ == '__main__':
    unittest.main()
