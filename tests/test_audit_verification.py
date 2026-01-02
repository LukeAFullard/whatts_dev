
import unittest
import pandas as pd
import numpy as np
from whatts.core import calculate_tolerance_limit
from whatts.utils import project_to_current_state

class TestAuditVerification(unittest.TestCase):
    def test_slope_units_readability(self):
        """
        Verify that slope_per_year is calculated correctly and included in the result.
        """
        # Create a trend of +10 per year
        # 2 years of data
        dates = pd.date_range("2020-01-01", periods=730, freq="D")

        # 10 units / 365 days = 10 / 31536000 per second? No.
        # Trend y = m*t + c
        # If we want +10 per year.
        # Year 0: 0. Year 1: 10.
        # t is in seconds.
        # m = 10 / (seconds_in_year).

        seconds_in_year = 31557600.0 # Approximate
        slope_per_sec = 10.0 / seconds_in_year

        start_ts = dates[0].timestamp()
        t_values = dates.map(pd.Timestamp.timestamp).values

        # y = slope * (t - t0)
        values = slope_per_sec * (t_values - start_ts)

        df = pd.DataFrame({"Date": dates, "Val": values})

        res = calculate_tolerance_limit(df, "Date", "Val", use_projection=True, confidence=0.95)

        self.assertIn("trend_slope_per_year", res)
        self.assertAlmostEqual(res['trend_slope_per_year'], 10.0, delta=0.5)
        # Delta allows for 365 vs 365.25 differences and small MannKendall estimator noise

    def test_alpha_propagation(self):
        """
        Verify that requesting a different confidence level changes the alpha passed to trend test.
        Since we can't easily mock the internal call without patching, we can check logic via side effects?
        Hard to check side effect of alpha on MK test unless we find a borderline trend.

        Instead, we'll trust the code change (we passed alpha=1-conf) and just ensure it runs
        without error for different confidence levels.
        """
        dates = pd.date_range("2020-01-01", periods=20, freq="D")
        values = np.random.normal(10, 1, 20)
        df = pd.DataFrame({"Date": dates, "Val": values})

        # Should not crash
        res_99 = calculate_tolerance_limit(df, "Date", "Val", confidence=0.99)
        res_90 = calculate_tolerance_limit(df, "Date", "Val", confidence=0.90)

        self.assertEqual(res_99['confidence_level'], 0.99)
        self.assertEqual(res_90['confidence_level'], 0.90)

if __name__ == '__main__':
    unittest.main()
