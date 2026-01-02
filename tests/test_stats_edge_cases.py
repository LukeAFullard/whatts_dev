import unittest
import numpy as np
from whatts.stats import wilson_score_upper_tolerance

class TestStatsEdgeCases(unittest.TestCase):
    def test_wilson_crash_perfect_compliance(self):
        """
        Regression test for crash when p_hat=1.0 (or 100% compliance)
        resulting in dist_from_top=0 and df=0 in chi2.
        """
        # Case 1: n=20, p_hat=1.0.
        # dist_from_top = 20 - 20 = 0.
        # This triggers chi2(alpha, 0) which returns NaN.
        try:
            utl = wilson_score_upper_tolerance(p_hat=1.0, n=20, n_eff=20, conf_level=0.95)
            self.assertFalse(np.isnan(utl), "UTL should not be NaN")
            self.assertEqual(utl, 1.0, "If p_hat is 1.0, UTL should be clamped to 1.0")
        except Exception as e:
            self.fail(f"wilson_score_upper_tolerance crashed with p_hat=1.0: {e}")

    def test_wilson_small_sample_perfect(self):
        # Case: n=5, p_hat=1.0
        utl = wilson_score_upper_tolerance(p_hat=1.0, n=5, n_eff=5, conf_level=0.95)
        self.assertFalse(np.isnan(utl))
        self.assertEqual(utl, 1.0)

    def test_wilson_small_sample_imperfect(self):
        # Case: n=10, p_hat=0.9 (1 failure)
        # dist = 1.
        utl = wilson_score_upper_tolerance(p_hat=0.9, n=10, n_eff=10, conf_level=0.95)
        # Should be > 0.9
        self.assertGreater(utl, 0.9)
        self.assertLessEqual(utl, 1.0)

if __name__ == '__main__':
    unittest.main()
