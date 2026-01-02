import pandas as pd
from .stats import (
    hazen_interpolate,
    calculate_neff_sum_corr,
    wilson_score_upper_tolerance
)
from .utils import project_to_current_state

def calculate_tolerance_limit(df, date_col, value_col, target_percentile=0.95, confidence=0.95):
    """
    Calculates the Upper Tolerance Limit (UTL) for compliance.

    Returns:
        dict: Results including the "Compare Value" (UTL).
    """
    # 1. Prep
    df = df.sort_values(by=date_col).copy()
    dates = pd.to_datetime(df[date_col])
    values = df[value_col].values
    n = len(values)

    if n < 10:
        raise ValueError("Sample size too small (n < 10).")

    # 2. Project
    proj_res = project_to_current_state(dates, values)
    analysis_data = proj_res['projected_data']

    # 3. Effective Sample Size
    n_eff = calculate_neff_sum_corr(analysis_data)

    # 4. Point Estimate (The "Face Value")
    point_est = hazen_interpolate(analysis_data, target_percentile)

    # 5. Upper Tolerance Limit (The "Regulatory Assurance Value")
    # Get the probability rank for the UTL
    utl_rank = wilson_score_upper_tolerance(
        p_hat=target_percentile,
        n=n,
        n_eff=n_eff,
        conf_level=confidence
    )

    # Map rank to value
    utl_value = hazen_interpolate(analysis_data, utl_rank)

    return {
        "statistic": f"{int(target_percentile*100)}th Percentile",
        "point_estimate": point_est,
        "upper_tolerance_limit": utl_value,  # THIS is the number to compare to the limit
        "confidence_level": confidence,
        "n_raw": n,
        "n_eff": n_eff,
        "trend_detected": proj_res['is_significant'],
        "trend_slope": proj_res['slope']
    }
