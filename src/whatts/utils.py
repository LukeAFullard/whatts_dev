import numpy as np
import pandas as pd
import MannKS  # The external dependency (Package name is mannks, but module is MannKS)

def project_to_current_state(dates, values, alpha=0.05):
    """
    Detects trend and projects data to the current (max) date.

    Args:
        dates (pd.Series): Datetime objects.
        values (np.array): Numeric values.
        alpha (float): Significance level for trend detection (default 0.05).

    Returns:
        dict: {
            'projected_data': np.array,
            'slope': float,             # Slope in units per second
            'slope_per_year': float,    # Slope in units per year (approx)
            'is_significant': bool,
            'p_value': float
        }
    """
    # 1. Run Mann-Kendall Test using MannKS package
    # MannKS.trend_test requires (values, times)
    # Times needs to be numeric. We'll use ordinal or similar relative to start.
    # To be precise, let's use seconds from epoch or ordinals.
    # The MannKS package handles time as numeric.

    date_numerics = dates.map(pd.Timestamp.timestamp).values

    # Run the test
    # mk_test_method='robust' is default, handles ties etc.
    mk_result = MannKS.trend_test(values, date_numerics, alpha=alpha)

    # Extract results
    # Based on exploration:
    # mk_result has attributes: p, slope, h (boolean significance)
    # The slope is in units per unit of time (seconds in our case).

    p_value = mk_result.p
    is_significant = bool(mk_result.h)
    slope_per_second = mk_result.slope # This is per unit of t (second)

    projected_values = values.copy()

    if is_significant:
        # Projection
        # P_t = V_t + Slope * (Time_Target - Time_t)

        target_time = np.max(date_numerics)
        time_diffs = target_time - date_numerics

        projected_values = values + slope_per_second * time_diffs

        # Physical clamp: Concentration cannot be < 0
        projected_values[projected_values < 0] = 0.0

        slope = slope_per_second

    else:
        slope = 0.0

    # Calculate slope per year for readability
    # 365.25 days * 24 * 3600 = 31,557,600 seconds
    seconds_per_year = 31557600.0
    slope_per_year = slope * seconds_per_year

    return {
        'projected_data': projected_values,
        'slope': slope, # Note: this is slope per SECOND
        'slope_per_year': slope_per_year,
        'is_significant': is_significant,
        'p_value': p_value
    }
