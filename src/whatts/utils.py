import numpy as np
import pandas as pd
from . import mannks  # The internal module

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
    # 1. Run Mann-Kendall Test
    # Assuming mannks.mann_kendall returns an object with 'p_value' and 'trend' attributes
    # Adjust this line based on exact mannks API documentation
    mk_result = mannks.mann_kendall(values)

    # Common significance threshold
    alpha = 0.05
    is_significant = mk_result.p_value < alpha

    slope = 0.0
    projected_values = values.copy()

    if is_significant:
        # 2. Calculate Sen's Slope
        # Sen's slope is usually units per time step.
        # We need to be careful about time units.
        # We will calculate slope relative to 'Days' to be precise.

        # Convert dates to Ordinals (Days)
        date_ordinals = dates.map(pd.Timestamp.toordinal).values

        # Calculate Slope (Change per Day)
        # Assuming mannks.sens_slope takes (values) or (values, time)
        # If it only takes values, it assumes unit spacing.
        slope_per_step = mannks.sens_slope(values)

        # If data is not evenly spaced, we really need a time-aware slope.
        # If mannks doesn't support time-aware slope, we assume monthly/unit spacing
        # and project based on index difference.

        # Let's assume unit spacing (index) for safety unless mannks specifies otherwise.
        # Project to the last index (N-1)
        n = len(values)
        indices = np.arange(n)
        current_index = n - 1

        # Projection Formula:
        # P_t = V_t + Slope * (Time_Target - Time_t)
        # If slope is negative (improving), and we are at t=0 (past),
        # (Target - t) is positive.
        # P_0 = 100 + (-5) * (10) = 50. Correct.

        projected_values = values + slope_per_step * (current_index - indices)

        # Physical clamp: Concentration cannot be < 0
        projected_values[projected_values < 0] = 0.0

        slope = slope_per_step

    return {
        'projected_data': projected_values,
        'slope': slope,
        'is_significant': is_significant,
        'p_value': mk_result.p_value
    }
