import unittest
import pandas as pd
import numpy as np
import warnings
from whatts import calculate_tolerance_limit

class TestWhattsFeedback(unittest.TestCase):
    def setUp(self):
        # Create standard test data
        dates = pd.date_range(start="2020-01-01", periods=50, freq="ME")
        np.random.seed(42)
        values = 100 - 0.5 * np.arange(50) + np.random.normal(0, 5, 50)
        self.df = pd.DataFrame({"Date": dates, "Value": values})

    def test_tau_and_p_value_returned(self):
        # Run calculation
        res = calculate_tolerance_limit(
            self.df, "Date", "Value", method='projection'
        )
        self.assertIn('tau', res)
        self.assertIn('p_value', res)
        # Check values are reasonable (should be trend detected)
        self.assertTrue(res['trend_detected'])
        self.assertIsNotNone(res['tau'])
        self.assertIsNotNone(res['p_value'])

    def test_missing_data_warning(self):
        # Create df with > 30% missing
        df_missing = self.df.copy()
        # Set 20 rows to NaN (out of 50, that's 40%)
        df_missing.loc[0:19, "Value"] = np.nan

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            calculate_tolerance_limit(df_missing, "Date", "Value")
            # Check for specific warning
            found = any("rows dropped due to missing values" in str(warn.message) for warn in w)
            self.assertTrue(found, "Warning for missing data not found")

    def test_constant_data_warning(self):
        # Create constant data
        df_const = self.df.copy()
        df_const["Value"] = 100.0

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            calculate_tolerance_limit(df_const, "Date", "Value")
            # Check for specific warning
            found = any("Data has zero variance" in str(warn.message) for warn in w)
            self.assertTrue(found, "Warning for constant data not found")

    def test_seasonal_period_qr(self):
        # QR method
        # We can't easily verify block size internally without mocking,
        # but we can ensure it runs without error when parameter is passed
        res = calculate_tolerance_limit(
            self.df, "Date", "Value", method='quantile_regression', seasonal_period=12
        )
        self.assertIn('method', res)
        self.assertEqual(res['method'], "Quantile Regression with Block Bootstrap")

if __name__ == '__main__':
    unittest.main()
