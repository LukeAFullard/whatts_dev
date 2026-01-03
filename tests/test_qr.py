import pandas as pd
import numpy as np
import pytest
from whatts.core import calculate_tolerance_limit

class TestQR:
    def test_qr_basic_execution(self):
        """
        Verifies that Quantile Regression runs without error and returns
        reasonable results for a simple linear trend.
        """
        # Create data with a clear linear trend
        # y = 10 + 0.1 * x (where x is days)
        # We need enough points for bootstrapping (user suggested N=30-60)
        n = 50
        dates = pd.date_range(start='2023-01-01', periods=n, freq='D')

        # Perfect line + small noise
        # 0.1 per day ~ 36.5 per year
        slope_per_day = 0.1
        values = 10.0 + slope_per_day * np.arange(n)

        # Add minimal noise to avoid degenerate bootstrap
        np.random.seed(42)
        values += np.random.normal(0, 0.5, n)

        df = pd.DataFrame({'date': dates, 'value': values})

        result = calculate_tolerance_limit(
            df, 'date', 'value',
            target_percentile=0.95,
            confidence=0.95,
            method='quantile_regression'
        )

        # Check keys
        assert result['method'] == "Quantile Regression with Block Bootstrap"
        assert result['statistic'] == "95th Percentile (QR modeled)"
        assert result['trend_slope'] is not None

        # Check slope estimation
        # Expected ~36.5 per year.
        # QR slope might vary slightly due to noise and percentile fitting,
        # but for a symmetric noise on a line, 95th percentile slope should be close to mean slope.
        # Actually, for 95th percentile, intercept is higher, but slope is same if variance is constant (homoscedastic).
        slope_est = result['trend_slope']
        assert 30 < slope_est < 45 # Rough bounds

        # Point estimate at end:
        # End is day 49. Value ~= 10 + 4.9 = 14.9.
        # 95th percentile of Normal(0, 0.5) is 1.645 * 0.5 = 0.82.
        # Expected point est ~= 14.9 + 0.82 = 15.72.
        pt_est = result['point_estimate']
        assert 14.0 < pt_est < 17.0

        # UTL should be higher than point estimate (since it's an upper confidence bound)
        # Note: In perfect compliance (100% fits), UTL might behave differently, but here we have variance.
        assert result['upper_tolerance_limit'] >= result['point_estimate']

    def test_qr_vs_projection(self):
        """
        Ensures both methods can be called on same data.
        """
        n = 40
        dates = pd.date_range(start='2023-01-01', periods=n, freq='D')
        values = np.linspace(10, 20, n) + np.random.normal(0, 1, n)
        df = pd.DataFrame({'date': dates, 'value': values})

        res_proj = calculate_tolerance_limit(df, 'date', 'value', method='projection')
        res_qr = calculate_tolerance_limit(df, 'date', 'value', method='quantile_regression')

        assert res_proj['point_estimate'] is not None
        assert res_qr['point_estimate'] is not None
        # They likely differ, but shouldn't be orders of magnitude apart for this simple case
        assert abs(res_proj['point_estimate'] - res_qr['point_estimate']) < 10.0

    def test_invalid_method(self):
        n = 10
        dates = pd.date_range(start='2023-01-01', periods=n, freq='D')
        values = np.linspace(10, 20, n)
        df = pd.DataFrame({'date': dates, 'value': values})

        with pytest.raises(ValueError, match="Unknown method"):
            calculate_tolerance_limit(df, 'date', 'value', method='magic_crystal_ball')

    def test_qr_target_date(self):
        """
        Verifies that QR projection respects the target_date argument.
        """
        n = 50
        dates = pd.date_range(start='2023-01-01', periods=n, freq='D')

        # Positive trend: 10 to 20
        values = np.linspace(10, 20, n)
        # Minimal noise
        np.random.seed(999)
        values += np.random.normal(0, 0.1, n)

        df = pd.DataFrame({'date': dates, 'value': values})

        # 1. Target = Start (should be around 10)
        res_start = calculate_tolerance_limit(
            df, 'date', 'value',
            method='quantile_regression',
            projection_target_date="start"
        )

        # 2. Target = End (should be around 20)
        res_end = calculate_tolerance_limit(
            df, 'date', 'value',
            method='quantile_regression',
            projection_target_date="end"
        )

        # The point estimate for "start" should be significantly lower than "end"
        assert res_start['point_estimate'] < res_end['point_estimate']

        # Start estimate ~ 10 + epsilon
        assert 9.0 < res_start['point_estimate'] < 12.0

        # End estimate ~ 20 + epsilon
        assert 19.0 < res_end['point_estimate'] < 22.0
