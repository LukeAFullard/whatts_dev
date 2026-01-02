import numpy as np
from scipy.stats import norm, chi2

def hazen_interpolate(data, target_rank):
    """
    Interpolates a value from 'data' at the specific 'target_rank' (0 to 1).
    """
    data_sorted = np.sort(data)
    n = len(data)
    hazen_ranks = (np.arange(1, n + 1) - 0.5) / n
    return np.interp(target_rank, hazen_ranks, data_sorted)

def inverse_hazen(data, value):
    """
    Finds the percentile rank (0 to 1) of a specific value within the data
    using Hazen plotting positions.
    """
    data_sorted = np.sort(data)
    n = len(data)

    # Hazen ranks for the sorted data
    hazen_ranks = (np.arange(1, n + 1) - 0.5) / n

    # We use interpolation to find the rank of 'value'
    # Note: np.interp expects x-coordinates to be sorted.
    # Here, data_sorted are the x-coordinates, hazen_ranks are the y-coordinates.
    # We set left=0.0 and right=1.0 to handle values outside the data range.
    rank = np.interp(value, data_sorted, hazen_ranks, left=0.0, right=1.0)

    return rank

def calculate_neff_sum_corr(data):
    """
    Calculates Effective Sample Size (n_eff) using Sum of Correlations.
    (Unchanged from v1)
    """
    n = len(data)
    if n < 3: return float(n)

    y = data - np.mean(data)
    var = np.var(y)

    # FIX: If variance is 0 (constant data), information is minimal.
    # Return 1.0 to represent a single effective observation.
    if var == 0: return 1.0

    sum_rho = 0.0
    for k in range(1, int(n / 2)):
        rho_k = np.sum(y[:-k] * y[k:]) / (n * var)
        if rho_k < 0: break
        sum_rho += rho_k * (1 - k/n)

    n_eff = n / (1 + 2 * sum_rho)
    return max(2.0, min(float(n), n_eff))

def score_test_probability(p_obs, p_null, n_eff):
    """
    Calculates the one-sided probability that the true proportion is <= p_null
    given an observed proportion p_obs.

    This is the direct counterpart to the Wilson Interval.

    Args:
        p_obs (float): The rank of the target value in the observed data.
        p_null (float): The regulatory target percentile (e.g., 0.95).
        n_eff (float): Effective sample size.

    Returns:
        float: Probability of compliance (0.0 to 1.0).
    """
    # Prevent division by zero if n_eff is weird
    if n_eff <= 0: return 0.0

    # Variance under the Null Hypothesis (Score Test standard)
    # This matches the Wilson Interval geometry.
    variance = (p_null * (1 - p_null)) / n_eff

    # Z-score calculation
    # Z = (Observed - Null) / StdDev
    z_score = (p_obs - p_null) / np.sqrt(variance)

    # Convert Z to probability (Cumulative Distribution Function)
    return norm.cdf(z_score)

def wilson_score_upper_tolerance(p_hat, n, n_eff=None, conf_level=0.95):
    """
    Calculates the One-Sided Upper Wilson Limit (Non-Parametric Upper Tolerance Limit).

    Args:
        p_hat (float): The target percentile (e.g., 0.95).
        n (int): Raw sample size (kept for API compatibility, but n_eff is used for logic).
        n_eff (float): Effective sample size (for variance).
        conf_level (float): Confidence level (default 0.95).

    Returns:
        float: The probability rank corresponding to the Upper Tolerance Limit.
    """
    if n_eff is None:
        n_eff = float(n)

    alpha = 1 - conf_level

    # --- CHANGE: One-Sided Z-Score ---
    # We use (1 - alpha), NOT (1 - alpha/2)
    z = norm.ppf(1 - alpha)

    # --- Standard Wilson Calculation ---
    denom = 1 + (z**2 / n_eff)
    center = (p_hat + (z**2 / (2 * n_eff)))

    term_inside_sqrt = (p_hat * (1 - p_hat) / n_eff) + (z**2 / (4 * n_eff**2))
    error_margin = np.sqrt(max(0.0, term_inside_sqrt))

    # We only care about the UPPER limit
    upper_lim = (center + z * error_margin) / denom

    # --- Boundary Corrections (One-Sided Logic) ---
    # We apply the Chi-Square correction if the sample size is small
    # and we are close to the boundary.

    # FIX: Use n_eff for boundary logic to account for autocorrelation.
    x_eff = p_hat * n_eff
    dist_from_top = n_eff - x_eff

    # Logic adapted from R 'binom.CI' but specific to Upper Limit
    # and adapted for Effective Sample Size.
    is_small = (n_eff <= 50 and dist_from_top <= 2)
    # FIX: Ensure no gap between 50 and 51 for float n_eff
    is_med = (50 < n_eff <= 100 and dist_from_top <= 3)

    if is_small or is_med:
        # Handle perfect compliance (dist_from_top <= 0)
        # If no failures observed (or implied), the upper bound is 1.0.
        if dist_from_top <= 0:
            upper_lim = 1.0
        else:
            # One-sided Chi-Square adjustment for upper bound
            # FIX: Use n_eff in denominator.
            upper_lim = 1.0 - 0.5 * chi2.ppf(alpha, 2 * dist_from_top) / n_eff

    return min(1.0, upper_lim)
