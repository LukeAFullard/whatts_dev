import pandas as pd
import numpy as np
import warnings
from .stats import (
    hazen_interpolate,
    calculate_neff_sum_corr,
    wilson_score_upper_tolerance,
    inverse_hazen,
    score_test_probability
)
from .utils import project_to_current_state
from .qr import fit_qr_current_state

def calculate_tolerance_limit(df, date_col, value_col, target_percentile=0.95, confidence=0.95,
                              regulatory_limit=None, use_projection=True, use_neff=True,
                              projection_target_date=None, method='projection', seasonal_period=None, n_boot=1000,
                              small_n_threshold=60, medium_n_threshold=120, distance_threshold=5):
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
        method (str): 'projection' (default) or 'quantile_regression'.
        seasonal_period (int): Optional minimum block size to respect seasonality (used in QR method).
        n_boot (int): Number of bootstrap iterations (default 1000) (used in QR method).
        small_n_threshold (int): N_eff threshold for 'small' sample boundary correction (default 60).
        medium_n_threshold (int): N_eff threshold for 'medium' sample boundary correction (default 120).
        distance_threshold (float): Expected observations above percentile to trigger correction (default 5).

    Returns:
        dict: Results including the "Compare Value" (UTL) and "Probability of Compliance".
              Also includes trend statistics 'tau' and 'p_value' if using 'projection' method.
    """
    # 1. Prep
    df = df.sort_values(by=date_col).copy()

    # Check for missing values
    missing_pct = df[value_col].isna().mean()
    if missing_pct > 0.3:
        warnings.warn(f"{missing_pct:.1%} of rows dropped due to missing values. Results may be unreliable.")

    # Drop NaNs from value_col
    df = df.dropna(subset=[value_col])

    dates = pd.to_datetime(df[date_col])
    values = df[value_col].values
    n = len(values)

    # Check for constant data (zero variance)
    if n > 1 and np.std(values) == 0:
        warnings.warn("Data has zero variance. Percentile estimates are uninformative.")

    if n < 5:
        raise ValueError("Sample size too small (n < 5).")

    if n < 10:
        warnings.warn(
            f"Sample size is very small (n={n}). "
            "Statistical results may be unstable or uninformative."
        )

    if method == 'quantile_regression':
        # --- PATH B: QUANTILE REGRESSION (The "Dynamic" Way) ---
        qr_res = fit_qr_current_state(
            dates, values,
            target_percentile=target_percentile,
            confidence=confidence,
            target_date=projection_target_date,
            seasonal_period=seasonal_period,
            n_boot=n_boot
        )

        return {
            "statistic": f"{int(target_percentile*100)}th Percentile (QR modeled)",
            "target_percentile": target_percentile,
            "point_estimate": qr_res['point_estimate'],
            "upper_tolerance_limit": qr_res['upper_tolerance_limit'],
            "confidence_level": confidence,
            "n_raw": n,
            "method": "Quantile Regression with Block Bootstrap",
            "trend_slope": qr_res['slope'],
            # The following keys are not applicable or computed differently in QR mode
            # We return them as None or defaults to maintain some consistency if needed by downstream tools,
            # or simply omit them. Based on user request, returning what is available.
            "trend_detected": True, # Implicitly modeling trend
            "trend_slope_per_year": qr_res['slope'],
            "probability_of_compliance": None, # Not implemented for QR yet
            "projected_data": None # Conceptually different
        }

    elif method == 'projection':
        # --- PATH A: PROJECTION (The "Stable" Way) ---
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
            # Extract additional metrics
            tau = proj_res['tau']
            p_value = proj_res['p_value']
        else:
            analysis_data = values
            # Default slope 0, is_significant False
            tau = None
            p_value = None

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
        utl_rank, wh_method = wilson_score_upper_tolerance(
            p_hat=target_percentile,
            n=n,
            n_eff=n_eff,
            conf_level=confidence,
            small_n_threshold=small_n_threshold,
            medium_n_threshold=medium_n_threshold,
            distance_threshold=distance_threshold
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
            "projected_data": analysis_data,
            "tau": tau,
            "p_value": p_value,
            "wh_method_used": wh_method
        }
    else:
        raise ValueError(f"Unknown method: {method}")

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
