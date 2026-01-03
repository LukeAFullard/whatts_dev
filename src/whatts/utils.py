import numpy as np
import pandas as pd
import MannKS  # The external dependency (Package name is mannks, but module is MannKS)

def project_to_current_state(dates, values, alpha=0.05, target_date=None):
    """
    Detects trend and projects data to the current (max) date or a specified target date.

    Args:
        dates (pd.Series): Datetime objects.
        values (np.array): Numeric values.
        alpha (float): Significance level for trend detection (default 0.05).
        target_date (datetime-like or str, optional): The date to project the values to.
            Defaults to the maximum date in the 'dates' series.
            Supported string aliases:
            - "start": Projects to the minimum date in the series.
            - "end" / "max" / "current": Projects to the maximum date.
            - "middle" / "center": Projects to the midpoint between min and max dates.

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

        min_time = np.min(date_numerics)
        max_time = np.max(date_numerics)

        if target_date is not None:
            if isinstance(target_date, str):
                target_date_lower = target_date.lower().strip()
                if target_date_lower == "start":
                    target_time = min_time
                elif target_date_lower in ["end", "max", "current"]:
                    target_time = max_time
                elif target_date_lower in ["middle", "center"]:
                    target_time = min_time + (max_time - min_time) / 2.0
                else:
                    # Try to parse string as date
                    target_time = pd.Timestamp(target_date).timestamp()
            else:
                target_time = pd.Timestamp(target_date).timestamp()
        else:
            target_time = max_time

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
