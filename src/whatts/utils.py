import numpy as np
import pandas as pd
import MannKS  # The external dependency (Package name is mannks, but module is MannKS)

def project_to_current_state(dates, values):
    """
    Detects trend and projects data to the current (max) date.

    Args:
        dates (pd.Series): Datetime objects.
        values (np.array): Numeric values.

    Returns:
        dict: {
            'projected_data': np.array,
            'slope': float,
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
    # alpha default is 0.05
    mk_result = MannKS.trend_test(values, date_numerics, alpha=0.05)

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

        # Convert slope to something more readable if needed, but for now we return raw slope
        # Maybe convert to per day or per year for the return dict for human readability?
        # The prompt implies returning the slope used.
        slope = slope_per_second

    else:
        slope = 0.0

    return {
        'projected_data': projected_values,
        'slope': slope, # Note: this is slope per SECOND
        'is_significant': is_significant,
        'p_value': p_value
    }
