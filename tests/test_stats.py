import unittest
import numpy as np
from whatts.stats import (
    hazen_interpolate,
    inverse_hazen,
    score_test_probability,
    wilson_score_upper_tolerance,
    wilson_score_interval, # Import the new function
    calculate_neff_sum_corr
)

class TestStats(unittest.TestCase):
    def test_hazen_interpolate_and_inverse(self):
        # Data: 1 to 10
        data = np.arange(1, 11, dtype=float)

        # Test interpolation
        # Rank 0.05 -> Value 1.0
        # hazen_interpolate now returns (value, note)
        val, note = hazen_interpolate(data, 0.05)
        self.assertAlmostEqual(val, 1.0)

        # Rank 0.95 -> Value 10.0
        val, note = hazen_interpolate(data, 0.95)
        self.assertAlmostEqual(val, 10.0)

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
        # This tests the backward compatibility alias which now only returns the upper limit (float)
        n = 30
        p_hat = 0.95

        # Updated: wilson_score_upper_tolerance now acts as an alias to wilson_score_interval
        # and returns a tuple (lower, upper, method)

        res = wilson_score_upper_tolerance(p_hat, n, n_eff=30, conf_level=0.95, sides=1)
        self.assertTrue(isinstance(res, tuple))
        self.assertEqual(len(res), 3)

        upper = res[1]
        self.assertTrue(isinstance(upper, float))
        self.assertTrue(p_hat < upper <= 1.0)

    def test_wilson_score_interval(self):
        # This tests the new full function
        n = 30
        p_hat = 0.95

        # Note: function now returns (lower, upper, method)
        lower, upper, method = wilson_score_interval(p_hat, n, n_eff=30, conf_level=0.95, sides=1)

        self.assertTrue(p_hat < upper <= 1.0)
        # Check method name is returned
        self.assertIn(method, ["Standard Wilson-Hazen", "Chi-Square Correction"])

        # Test with low n_eff
        _, upper_low_neff, _ = wilson_score_interval(p_hat, n, n_eff=5, conf_level=0.95, sides=1)
        # Lower n_eff should result in wider interval (higher UTL rank)
        self.assertTrue(upper_low_neff >= upper)

    def test_two_sided_confidence_interval(self):
        # Test Two-Sided Interval (sides=2)
        # Use N=60 to trigger Chi-Square Correction (D=3 <= 5)
        n = 60
        p_hat = 0.95

        # 1-Sided 95% - use the full function
        _, upper_1s, method1 = wilson_score_interval(p_hat, n, conf_level=0.95, sides=1)
        self.assertEqual(method1, "Chi-Square Correction")

        # 2-Sided 95%
        # The upper bound should correspond to 97.5% quantile of distribution, so it should be HIGHER than 1-sided 95%
        _, upper_2s, method2 = wilson_score_interval(p_hat, n, conf_level=0.95, sides=2)
        self.assertEqual(method2, "Chi-Square Correction")

        self.assertTrue(upper_2s > upper_1s)

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
