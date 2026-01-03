import pandas as pd
import numpy as np
import pytest
from whatts.core import calculate_tolerance_limit

class TestTrendProjection:
    def test_trend_projection_aliases(self):
        # 1. Create data with a strong positive trend
        # 10 points, 1 per day. Range: 2023-01-01 to 2023-01-10
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        # Values: 10, 12, 14, ..., 28. Slope = 2.
        values = np.linspace(10, 28, 10)

        df = pd.DataFrame({'date': dates, 'value': values})

        # Test "start"
        result_start = calculate_tolerance_limit(
            df, 'date', 'value',
            target_percentile=0.95,
            confidence=0.95,
            use_projection=True,
            use_neff=False,
            projection_target_date="start"
        )
        # Should project to first value (10)
        np.testing.assert_allclose(result_start['projected_data'], 10.0, atol=0.1)

        # Test "end"
        result_end = calculate_tolerance_limit(
            df, 'date', 'value',
            target_percentile=0.95,
            confidence=0.95,
            use_projection=True,
            use_neff=False,
            projection_target_date="end"
        )
        # Should project to last value (28)
        np.testing.assert_allclose(result_end['projected_data'], 28.0, atol=0.1)

        # Test "middle"
        result_mid = calculate_tolerance_limit(
            df, 'date', 'value',
            target_percentile=0.95,
            confidence=0.95,
            use_projection=True,
            use_neff=False,
            projection_target_date="middle"
        )
        # Middle value is 19.
        np.testing.assert_allclose(result_mid['projected_data'], 19.0, atol=0.1)

    def test_trend_projection_custom_date(self):
        # Create data
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        values = np.linspace(10, 28, 10)
        df = pd.DataFrame({'date': dates, 'value': values})

        # Target date 5 days before start
        target = pd.Timestamp('2022-12-27')
        # Slope is 2 per day. 5 days back from 10 is 0.

        result = calculate_tolerance_limit(
            df, 'date', 'value',
            target_percentile=0.95,
            confidence=0.95,
            use_projection=True,
            use_neff=False,
            projection_target_date=target
        )

        np.testing.assert_allclose(result['projected_data'], 0.0, atol=0.1)
