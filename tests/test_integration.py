import unittest
import pandas as pd
import numpy as np
import warnings
from whatts import calculate_tolerance_limit, compare_compliance_methods

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Generate mock data: Trending downwards (improving)
        np.random.seed(42)
        n = 50
        trend = np.linspace(100, 50, n)
        noise = np.random.normal(0, 5, n)
        self.values = trend + noise
        self.dates = pd.date_range(start="2020-01-01", periods=n, freq="ME")
        self.df = pd.DataFrame({"Date": self.dates, "Val": self.values})

    def test_calculate_tolerance_limit_basics(self):
        res = calculate_tolerance_limit(self.df, "Date", "Val")

        self.assertIn("point_estimate", res)
        self.assertIn("upper_tolerance_limit", res)
        self.assertIn("n_eff", res)
        self.assertIn("trend_slope", res)

        self.assertTrue(res['trend_detected'])
        self.assertTrue(res['trend_slope'] < 0)

    def test_options(self):
        # Disable projection
        res_no_proj = calculate_tolerance_limit(
            self.df, "Date", "Val", use_projection=False
        )
        self.assertFalse(res_no_proj['trend_detected'])
        self.assertEqual(res_no_proj['trend_slope'], 0.0)

        # Disable neff
        res_no_neff = calculate_tolerance_limit(
            self.df, "Date", "Val", use_neff=False
        )
        self.assertEqual(res_no_neff['n_eff'], 50.0)

    def test_comparison_table(self):
        comp = compare_compliance_methods(self.df, "Date", "Val")
        self.assertEqual(len(comp), 3)
        methods = comp["Method"].tolist()
        self.assertIn("Naive", methods)
        self.assertIn("Detrended Only", methods)
        self.assertIn("Full whatts", methods)

    def test_compliance_probability(self):
        # Limit = 200 (way above data) -> High prob
        res_high = calculate_tolerance_limit(
            self.df, "Date", "Val", regulatory_limit=200
        )
        self.assertIsNotNone(res_high['probability_of_compliance'])

        print(f"\nDEBUG: Compliance Prob High: {res_high['probability_of_compliance']}")

        self.assertTrue(res_high['probability_of_compliance'] > 0.90)

        # Limit = 0 (way below data) -> Low prob
        res_low = calculate_tolerance_limit(
            self.df, "Date", "Val", regulatory_limit=0
        )
        self.assertTrue(res_low['probability_of_compliance'] < 0.01)

    def test_warning_low_neff(self):
        # Create very small dataset (n=5). n_eff must be <= 5.
        small_df = self.df.iloc[:5].copy()

        # Verify n_eff is low
        # Note: calculate_tolerance_limit raises ValueError if n < 10.
        # So we need n >= 10, but n_eff < 10.

        # Use a slice of 15.
        med_df = self.df.iloc[:15].copy()

        # With high autocorrelation (or just random), n_eff usually drops.
        # Let's force high correlation manually to ensure n_eff drops.
        # But wait, self.values has noise.
        # Let's make a new dataset with n=15 and perfectly repeated values.
        # If values are repeated, variance is 0? No.
        # 1, 2, 1, 2...

        vals = np.tile([10, 10.1], 10) # 20 values
        dates = pd.date_range("2020-01-01", periods=20, freq="D")
        df_corr = pd.DataFrame({"D": dates, "V": vals})

        # With this alternating pattern, correlation might be weird.
        # Let's just use the `calculate_neff_sum_corr` behavior:
        # If we use white noise, n_eff ~ n.
        # If we use AR(1) with rho=0.9.

        np.random.seed(99)
        ar_vals = np.zeros(20)
        for i in range(1, 20):
            ar_vals[i] = 0.95 * ar_vals[i-1] + np.random.normal(0, 0.1)

        df_ar = pd.DataFrame({"D": dates, "V": ar_vals})

        res = calculate_tolerance_limit(df_ar, "D", "V")
        print(f"\nDEBUG: AR(1) N_eff: {res['n_eff']}")
        self.assertTrue(res['n_eff'] < 10)

    def test_nan_handling(self):
        """
        Verify that NaNs in the value column are ignored and result matches
        clean data.
        """
        # Take the base dataframe
        clean_df = self.df.copy()
        clean_res = calculate_tolerance_limit(clean_df, "Date", "Val")

        # Create a dataframe with NaNs interspersed
        dirty_df = self.df.copy()
        # Insert NaNs at indices 5, 15, 25
        dirty_df.loc[5, "Val"] = np.nan
        dirty_df.loc[15, "Val"] = np.nan
        dirty_df.loc[25, "Val"] = np.nan

        # We also need to add extra rows to dirty_df so that after dropping NaNs,
        # it still has the same data as clean_df.
        # Actually, simpler: create clean_df as a subset of dirty_df (without the NaNs rows).

        # Strategy:
        # 1. Create Data with NaNs.
        # 2. Create Data with NaNs dropped manually.
        # 3. Compare results.

        dates_nan = pd.date_range("2020-01-01", periods=60, freq="D")
        values_nan = np.random.normal(100, 10, 60)
        # Add NaNs
        values_nan[10] = np.nan
        values_nan[20] = np.nan
        values_nan[30] = np.nan

        df_dirty = pd.DataFrame({"Date": dates_nan, "Val": values_nan})
        df_clean = df_dirty.dropna().copy()

        res_dirty = calculate_tolerance_limit(df_dirty, "Date", "Val")
        res_clean = calculate_tolerance_limit(df_clean, "Date", "Val")

        self.assertAlmostEqual(res_dirty['point_estimate'], res_clean['point_estimate'])
        self.assertAlmostEqual(res_dirty['upper_tolerance_limit'], res_clean['upper_tolerance_limit'])
        self.assertAlmostEqual(res_dirty['n_eff'], res_clean['n_eff'])
        self.assertEqual(res_dirty['n_raw'], res_clean['n_raw'])


if __name__ == '__main__':
    unittest.main()
