import numpy as np
import pandas as pd
import statsmodels.api as sm
from .bootstrap import generate_block_bootstraps

def fit_qr_current_state(dates, values, target_percentile=0.95, confidence=0.95):
    """
    Fits Quantile Regression and estimates the Current State (final date)
    using Block Bootstrapping for uncertainty.

    Returns:
        dict: {
            'point_estimate': float,
            'upper_tolerance_limit': float,
            'slope': float
        }
    """
    # 1. Prepare Data
    # Convert dates to Ordinals or fractional years
    # Standardize to avoid huge numbers in regression
    t_start = dates.min()
    t_numeric = (dates - t_start).dt.days.values # X variable
    y = values # Y variable

    # Target date for prediction (The "Current State")
    t_final = t_numeric.max()

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
    boot_gen = generate_block_bootstraps(y, t_numeric, n_boot=1000)

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

    # 4. Calculate Upper Tolerance Limit
    # We want the 95th percentile of the bootstrap distribution
    # (This effectively gives the 95% Upper Confidence Bound of the 95th Percentile)
    bootstrap_preds = np.array(bootstrap_preds)

    # Check if we have enough successful bootstraps
    if len(bootstrap_preds) < 100:
        raise ValueError("Quantile Regression Bootstrap failed to converge.")

    utl_rank = confidence # e.g. 0.95
    upper_limit = np.percentile(bootstrap_preds, utl_rank * 100)

    return {
        "point_estimate": point_est,
        "upper_tolerance_limit": upper_limit,
        "slope": slope_point * 365.25, # Convert to per-year for reporting
        "bootstrap_distribution": bootstrap_preds # Useful for plotting
    }
