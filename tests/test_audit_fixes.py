import unittest
import numpy as np
from whatts.stats import calculate_neff_sum_corr, wilson_score_upper_tolerance

class TestAuditFixes(unittest.TestCase):
    def test_neff_constant_zero_variance(self):
        """
        Verify that constant data returns n_eff=1.0 (minimal info), not n.
        """
        data = np.ones(50) * 10.0
        neff = calculate_neff_sum_corr(data)
        self.assertEqual(neff, 1.0, "Constant data should have n_eff=1.0")

    def test_wilson_boundary_correction_uses_neff(self):
        """
        Verify that small n_eff triggers the Chi-Square correction
        and uses n_eff in the formula, resulting in a wider interval (higher rank)
        than if n was used.
        """
        n = 30
        n_eff = 15.0 # Autocorrelated
        p_hat = 0.95
        conf = 0.95

        # Calculate with n_eff passed correctly
        _, utl_rank_corr, _ = wilson_score_upper_tolerance(p_hat, n, n_eff=n_eff, conf_level=conf)

        # Calculate as if independent (n=15)
        _, utl_rank_indep_small, _ = wilson_score_upper_tolerance(p_hat, 15, n_eff=15, conf_level=conf)

        # Calculate as if independent (n=30) - this was the "bugged" behavior if it used 'n'
        _, utl_rank_indep_large, _ = wilson_score_upper_tolerance(p_hat, 30, n_eff=30, conf_level=conf)

        # The corrected version (n_eff=15) should match the independent version with n=15
        # because the formula now consistently uses n_eff.
        self.assertAlmostEqual(utl_rank_corr, utl_rank_indep_small)

        # And it should be significantly different (wider/higher) than n=30
        self.assertNotAlmostEqual(utl_rank_corr, utl_rank_indep_large)
        self.assertGreater(utl_rank_corr, utl_rank_indep_large)

if __name__ == '__main__':
    unittest.main()
