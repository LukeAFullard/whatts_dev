import numpy as np
import pandas as pd
import statsmodels.api as sm
from .bootstrap import generate_block_bootstraps

def fit_qr_current_state(dates, values, target_percentile=0.95, confidence=0.95, target_date=None, seasonal_period=None, n_boot=1000, sides=2):
    """
    Fits Quantile Regression and estimates the Current State (final date)
    using Block Bootstrapping for uncertainty.

    Args:
        dates (pd.Series): Datetime objects.
        values (np.array): Numeric values.
        target_percentile (float): The quantile to fit (default 0.95).
        confidence (float): Confidence level for the UTL (default 0.95).
        target_date (datetime-like or str, optional): The date/point to predict at.
            Defaults to the maximum date (end of series).
            Supports aliases: "start", "middle", "end".
        seasonal_period (int): Optional minimum block size to respect seasonality.
        n_boot (int): Number of bootstrap iterations (default 1000).
        sides (int): 1 for One-Sided Limit, 2 for Two-Sided Interval (default 2).

    Returns:
        dict: {
            'point_estimate': float,
            'upper_tolerance_limit': float,
            'lower_tolerance_limit': float,
            'slope': float
        }
    """
    # 1. Prepare Data
    # Convert dates to Ordinals or fractional years
    # Standardize to avoid huge numbers in regression
    t_start = dates.min()
    if isinstance(dates, pd.Series):
        t_numeric = (dates - t_start).dt.days.values
    else:
        # Fallback if it's an Index or something else
        t_numeric = (dates - t_start).days.values

    # Ensure t_numeric is numpy array
    if not isinstance(t_numeric, np.ndarray):
        t_numeric = np.array(t_numeric)

    y = values # Y variable

    # Resolve Target Date
    # Note: t_numeric is in days relative to t_start (0 to max)
    max_days = t_numeric.max()
    min_days = 0.0

    if target_date is not None:
        if isinstance(target_date, str):
            target_date_lower = target_date.lower().strip()
            if target_date_lower == "start":
                t_final = min_days
            elif target_date_lower in ["end", "max", "current"]:
                t_final = max_days
            elif target_date_lower in ["middle", "center"]:
                t_final = (min_days + max_days) / 2.0
            else:
                # Try to parse string as date
                target_ts = pd.Timestamp(target_date)
                t_final = (target_ts - t_start).days
        else:
            target_ts = pd.Timestamp(target_date)
            t_final = (target_ts - t_start).days
    else:
        t_final = max_days

    # 2. Fit Point Estimate (The "Face Value")
    # Add constant for intercept: y = a + bx
    X = sm.add_constant(t_numeric)

    model = sm.QuantReg(y, X)
    result = model.fit(q=target_percentile)

    # Predict at t_final
    # params[0] is intercept, params[1] is slope
    point_est = result.params[0] + result.params[1] * t_final
    slope_point = result.params[1]

    # 3. Bootstrap for Uncertainty (The "Regulatory Assurance")
    # We want the Upper Confidence Limit of this prediction.
    bootstrap_preds = []

    # Create generator
    boot_gen = generate_block_bootstraps(y, t_numeric, n_boot=n_boot, seasonal_period=seasonal_period)

    for y_boot, x_boot in boot_gen:
        try:
            # Fit QR on bootstrapped data
            X_boot = sm.add_constant(x_boot)
            mod_boot = sm.QuantReg(y_boot, X_boot)
            res_boot = mod_boot.fit(q=target_percentile)

            # Predict at t_final (ALWAYS predict at the original final time)
            pred = res_boot.params[0] + res_boot.params[1] * t_final
            bootstrap_preds.append(pred)
        except:
            # QR convergence can fail on small bootstraps with few distinct values
            continue

    # 4. Calculate Tolerance Limits
    # We want the percentiles of the bootstrap distribution of the point prediction.
    bootstrap_preds = np.array(bootstrap_preds)

    # Check if we have enough successful bootstraps
    if len(bootstrap_preds) < 100 and n_boot >= 100:
        raise ValueError("Quantile Regression Bootstrap failed to converge.")
    elif len(bootstrap_preds) == 0:
        raise ValueError("Quantile Regression Bootstrap failed to converge (0 successes).")

    alpha = 1.0 - confidence
    alpha_tail = alpha / sides

    # Upper Limit Rank: 1 - alpha_tail
    # e.g. 95% conf, 2-sided -> alpha=0.05, tail=0.025 -> rank=0.975
    # e.g. 95% conf, 1-sided -> alpha=0.05, tail=0.05 -> rank=0.95
    upper_rank = 1.0 - alpha_tail
    lower_rank = alpha_tail

    upper_limit = np.percentile(bootstrap_preds, upper_rank * 100)
    lower_limit = np.percentile(bootstrap_preds, lower_rank * 100)

    return {
        "point_estimate": point_est,
        "upper_tolerance_limit": upper_limit,
        "lower_tolerance_limit": lower_limit,
        "slope": slope_point * 365.25, # Convert to per-year for reporting
        "bootstrap_distribution": bootstrap_preds # Useful for plotting
    }
