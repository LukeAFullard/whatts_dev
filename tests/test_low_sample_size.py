
import unittest
import pandas as pd
import numpy as np
import warnings
from whatts.core import calculate_tolerance_limit

class TestLowSampleSize(unittest.TestCase):
    def test_sample_size_too_small(self):
        """
        Verify that n < 5 raises ValueError.
        """
        dates = pd.date_range("2020-01-01", periods=4, freq="D")
        values = np.random.normal(10, 1, 4)
        df = pd.DataFrame({"Date": dates, "Val": values})

        with self.assertRaisesRegex(ValueError, "Sample size too small"):
            calculate_tolerance_limit(df, "Date", "Val")

    def test_sample_size_warning(self):
        """
        Verify that 5 <= n < 10 raises a warning but returns a result.
        """
        dates = pd.date_range("2020-01-01", periods=6, freq="D")
        values = np.random.normal(10, 1, 6)
        df = pd.DataFrame({"Date": dates, "Val": values})

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            res = calculate_tolerance_limit(df, "Date", "Val")

            # Check for the specific warning
            found = any("Sample size is very small" in str(warn.message) for warn in w)
            self.assertTrue(found, "Expected warning about small sample size (n=6) not found")

            # Result should be valid
            self.assertIn("upper_tolerance_limit", res)
            self.assertEqual(res['n_raw'], 6)

    def test_sample_size_no_warning_high_n(self):
        """
        Verify that n >= 10 does NOT raise the *sample size* warning.
        (It might raise n_eff warning if data is correlated, so we check specific msg)
        """
        dates = pd.date_range("2020-01-01", periods=12, freq="D")
        values = np.random.normal(10, 1, 12)
        df = pd.DataFrame({"Date": dates, "Val": values})

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            calculate_tolerance_limit(df, "Date", "Val")

            found = any("Sample size is very small" in str(warn.message) for warn in w)
            self.assertFalse(found, "Should not warn about sample size for n=12")

if __name__ == '__main__':
    unittest.main()
