import pandas as pd
import warnings
from .stats import (
    hazen_interpolate,
    calculate_neff_sum_corr,
    wilson_score_upper_tolerance,
    inverse_hazen,
    score_test_probability
)
from .utils import project_to_current_state

def calculate_tolerance_limit(df, date_col, value_col, target_percentile=0.95, confidence=0.95,
                              regulatory_limit=None, use_projection=True, use_neff=True,
                              projection_target_date=None):
    """
    Calculates the Upper Tolerance Limit (UTL) for compliance and optionally the Probability of Compliance.

    Note:
        Rows with missing values (NaN) in the `value_col` are dropped prior to analysis.
        The effective sample size and trend detection are calculated based on the
        remaining available data points, ignoring the time gaps caused by missing data.

    Args:
        df (pd.DataFrame): Input dataframe.
        date_col (str): Column name for dates.
        value_col (str): Column name for values.
        target_percentile (float): The percentile to calculate (default 0.95).
        confidence (float): Confidence level for the tolerance limit (default 0.95).
        regulatory_limit (float, optional): The regulatory threshold to compare against.
        use_projection (bool): Whether to project data to current state using trends (default True).
        use_neff (bool): Whether to adjust for autocorrelation using effective sample size (default True).
        projection_target_date (datetime-like, optional): Date to project the trend to (default is max date).

    Returns:
        dict: Results including the "Compare Value" (UTL) and "Probability of Compliance".
    """
    # 1. Prep
    df = df.sort_values(by=date_col).copy()

    # Drop NaNs from value_col
    df = df.dropna(subset=[value_col])

    dates = pd.to_datetime(df[date_col])
    values = df[value_col].values
    n = len(values)

    if n < 5:
        raise ValueError("Sample size too small (n < 5).")

    if n < 10:
        warnings.warn(
            f"Sample size is very small (n={n}). "
            "Statistical results may be unstable or uninformative."
        )

    # 2. Project (if enabled)
    slope = 0.0
    slope_per_year = 0.0
    is_significant = False

    if use_projection:
        # Pass the confidence level (as alpha) to the trend test for consistency
        alpha = 1.0 - confidence
        proj_res = project_to_current_state(dates, values, alpha=alpha, target_date=projection_target_date)
        analysis_data = proj_res['projected_data']
        slope = proj_res['slope']
        slope_per_year = proj_res['slope_per_year']
        is_significant = proj_res['is_significant']
    else:
        analysis_data = values
        # Default slope 0, is_significant False

    # 3. Effective Sample Size (if enabled)
    if use_neff:
        n_eff = calculate_neff_sum_corr(analysis_data)

        # Minimum Record Length Warning
        if n_eff < 10:
            warnings.warn(
                f"Effective Sample Size is extremely low ({n_eff:.1f}). "
                "Compliance results will have very wide confidence intervals "
                "and may be uninformative."
            )
    else:
        n_eff = float(n)

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

    # 6. Probability of Compliance
    compliance_prob = None
    if regulatory_limit is not None:
        # A. Find where the limit sits in our projected data
        obs_rank = inverse_hazen(analysis_data, regulatory_limit)

        # B. Calculate probability that True Target Percentile <= Limit
        compliance_prob = score_test_probability(
            p_obs=obs_rank,
            p_null=target_percentile,
            n_eff=n_eff
        )

    return {
        "statistic": f"{int(target_percentile*100)}th Percentile",
        "target_percentile": target_percentile,
        "point_estimate": point_est,
        "upper_tolerance_limit": utl_value,  # THIS is the number to compare to the limit
        "confidence_level": confidence,
        "n_raw": n,
        "n_eff": n_eff,
        "trend_detected": is_significant,
        "trend_slope": slope,
        "trend_slope_per_year": slope_per_year,
        "probability_of_compliance": compliance_prob,
        "projected_data": analysis_data
    }

def compare_compliance_methods(df, date_col, value_col, target_percentile=0.95, confidence=0.95, regulatory_limit=None, projection_target_date=None):
    """
    Runs the assessment three ways:
    1. Naive: Raw data, Standard Wilson-Hazen (use_projection=False, use_neff=False)
    2. Detrended Only: Projected data, Standard Wilson-Hazen (use_projection=True, use_neff=False)
    3. Full whatts: Projected data + n_eff correction (use_projection=True, use_neff=True)

    Returns:
        pd.DataFrame: A comparison table.
    """

    scenarios = [
        {"name": "Naive", "use_projection": False, "use_neff": False},
        {"name": "Detrended Only", "use_projection": True, "use_neff": False},
        {"name": "Full whatts", "use_projection": True, "use_neff": True},
    ]

    results = []

    for sc in scenarios:
        res = calculate_tolerance_limit(
            df, date_col, value_col, target_percentile, confidence, regulatory_limit,
            use_projection=sc["use_projection"], use_neff=sc["use_neff"],
            projection_target_date=projection_target_date
        )

        row = {
            "Method": sc["name"],
            "Point Estimate": res["point_estimate"],
            "Upper Tolerance Limit": res["upper_tolerance_limit"],
            "N_eff": res["n_eff"],
            "Trend Slope": res["trend_slope"],
            "Trend Slope (Yearly)": res["trend_slope_per_year"]
        }

        if regulatory_limit is not None:
            row["Probability of Compliance"] = res["probability_of_compliance"]

        results.append(row)

    return pd.DataFrame(results)
