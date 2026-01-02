import pandas as pd
import numpy as np
from .stats import (
    hazen_interpolate,
    calculate_neff_sum_corr,
    wilson_score_interval_corrected
)
from .utils import project_to_current_state

def calculate_compliance(df, date_col, value_col, target_percentile=0.95):
    """
    Main entry point for calculating compliance statistics.

    Args:
        df (pd.DataFrame): Input dataframe.
        date_col (str): Column name for dates.
        value_col (str): Column name for values.
        target_percentile (float): The percentile to calculate (default 0.95).

    Returns:
        dict: Comprehensive results dictionary.
    """
    # 1. Data Prep
    df = df.sort_values(by=date_col).copy()
    dates = pd.to_datetime(df[date_col])
    values = df[value_col].values
    n = len(values)

    if n < 10:
        raise ValueError("Sample size too small for reliable analysis (n < 10).")

    # 2. Project to Current State
    projection_result = project_to_current_state(dates, values)
    analysis_data = projection_result['projected_data']

    # 3. Calculate Effective Sample Size (n_eff)
    # We calculate this on the *projected* data (which represents residuals around current state)
    n_eff = calculate_neff_sum_corr(analysis_data)

    # 4. Point Estimate (Hazen)
    # We look for the 95th percentile concentration
    point_estimate = hazen_interpolate(analysis_data, target_percentile)

    # 5. Confidence Interval (Rank Wilson)
    # A. Get probability bounds
    p_lower, p_upper = wilson_score_interval_corrected(
        p_hat=target_percentile,
        n=n,
        n_eff=n_eff
    )

    # B. Map probabilities to concentrations
    ci_lower_val = hazen_interpolate(analysis_data, p_lower)
    ci_upper_val = hazen_interpolate(analysis_data, p_upper)

    return {
        "statistic_name": f"{int(target_percentile*100)}th Percentile",
        "value": point_estimate,
        "conf_interval": (ci_lower_val, ci_upper_val),
        "ci_probabilities": (p_lower, p_upper),
        "n_raw": n,
        "n_eff": n_eff,
        "trend_significant": projection_result['is_significant'],
        "trend_slope": projection_result['slope'],
        "method": "Wilson-Hazen (Corrected) on Projected Data"
    }
