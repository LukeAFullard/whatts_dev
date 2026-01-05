import numpy as np
from scipy.stats import norm, chi2

def hazen_interpolate(data, target_rank, min_value=None, max_value=None):
    """
    Interpolates a value from 'data' at the specific 'target_rank' (0 to 1)
    using Probit (Z-score) interpolation to handle tail curvature and extrapolation.

    Args:
        data (array-like): Input data values.
        target_rank (float): The percentile rank to estimate (0-1).
        min_value (float, optional): Minimum allowed physical value (clamping).
        max_value (float, optional): Maximum allowed physical value (clamping).

    Returns:
        tuple: (value, clamped_note)
            value (float): The interpolated/extrapolated value.
            clamped_note (str): "None", "Min Clamped", or "Max Clamped".
    """
    data_sorted = np.sort(data)
    n = len(data)
    hazen_ranks = (np.arange(1, n + 1) - 0.5) / n

    # --- CHANGE: Probit Interpolation ---
    # Instead of linear interpolation on p (flat tails), we interpolate on Z (curved tails).
    # This also allows extrapolation beyond the data range.

    # Transform Hazen ranks to Z-scores
    z_scores = norm.ppf(hazen_ranks)

    # Transform target rank to target Z
    # Clamp rank to avoid infinity, though Hazen avoids 0/1 for the data ranks.
    # Floating point precision limits: ~1e-16 is epsilon, so 1e-9 is safe.
    safe_rank = np.clip(target_rank, 1e-9, 1.0 - 1e-9)
    z_target = norm.ppf(safe_rank)

    # Handle small n (cannot extrapolate with slope)
    if n < 2:
        val = data_sorted[0]
    elif z_target > z_scores[-1]:
        # Upper Tail Extrapolation
        # Slope determined by last two points
        slope = (data_sorted[-1] - data_sorted[-2]) / (z_scores[-1] - z_scores[-2])
        val = data_sorted[-1] + slope * (z_target - z_scores[-1])
    elif z_target < z_scores[0]:
        # Lower Tail Extrapolation
        # Slope determined by first two points
        slope = (data_sorted[1] - data_sorted[0]) / (z_scores[1] - z_scores[0])
        val = data_sorted[0] + slope * (z_target - z_scores[0])
    else:
        # Interpolation (Piecewise Linear in Z-space)
        val = np.interp(z_target, z_scores, data_sorted)

    # Apply Clamping
    clamped_note = "None"
    if min_value is not None and val < min_value:
        val = min_value
        clamped_note = "Min Clamped"
    elif max_value is not None and val > max_value:
        val = max_value
        clamped_note = "Max Clamped"

    return val, clamped_note

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

def wilson_score_interval(p_hat, n, n_eff=None, conf_level=0.95, sides=2,
                          small_n_threshold=60, medium_n_threshold=120, distance_threshold=5):
    """
    Calculates the Wilson Score Interval (Non-Parametric Tolerance Limit) for a percentile.

    Args:
        p_hat (float): The target percentile (e.g., 0.95).
        n (int): Raw sample size (kept for API compatibility, but n_eff is used for logic).
        n_eff (float): Effective sample size (for variance).
        conf_level (float): Confidence level (default 0.95).
        sides (int): 1 for One-Sided Limit, 2 for Two-Sided Interval (default 2).
        small_n_threshold (int): N_eff threshold for 'small' sample logic (default 60).
        medium_n_threshold (int): N_eff threshold for 'medium' sample logic (default 120).
        distance_threshold (float): Expected observations above percentile to trigger correction (default 5).

    Returns:
        tuple: (lower_lim, upper_lim, method_used)
    """
    if n_eff is None:
        n_eff = float(n)

    alpha = 1 - conf_level
    alpha_tail = alpha / sides

    # --- Z-Score based on sides ---
    z = norm.ppf(1 - alpha_tail)

    # --- Standard Wilson Calculation ---
    denom = 1 + (z**2 / n_eff)
    center = (p_hat + (z**2 / (2 * n_eff)))

    term_inside_sqrt = (p_hat * (1 - p_hat) / n_eff) + (z**2 / (4 * n_eff**2))
    error_margin = np.sqrt(max(0.0, term_inside_sqrt))

    lower_lim = (center - z * error_margin) / denom
    upper_lim = (center + z * error_margin) / denom

    # --- Boundary Corrections (Upper Logic Only implemented for Chi-Square) ---
    # We apply the Chi-Square correction if the sample size is small
    # and we are close to the boundary.

    # FIX: Use n_eff for boundary logic to account for autocorrelation.
    # Expected observations "above" the target percentile
    dist_from_top = n_eff * (1 - p_hat)

    # Expanded Chi-Square Logic:

    # 1. Upper Bound Logic
    is_small_top = (n_eff <= small_n_threshold and dist_from_top <= distance_threshold)
    is_med_top = (small_n_threshold < n_eff <= medium_n_threshold and dist_from_top <= distance_threshold)

    method_used = "Standard Wilson-Hazen"

    if is_small_top or is_med_top:
        method_used = "Chi-Square Correction"
        if dist_from_top <= 0:
            upper_lim = 1.0
        else:
            # Chi-Square adjustment for upper bound
            upper_lim = 1.0 - 0.5 * chi2.ppf(alpha_tail, 2 * dist_from_top) / n_eff

    # 2. Lower Bound Logic
    dist_from_bottom = n_eff * p_hat
    is_small_bot = (n_eff <= small_n_threshold and dist_from_bottom <= distance_threshold)
    is_med_bot = (small_n_threshold < n_eff <= medium_n_threshold and dist_from_bottom <= distance_threshold)

    if is_small_bot or is_med_bot:
        method_used = "Chi-Square Correction" # Flag if either triggered
        if dist_from_bottom <= 0:
            lower_lim = 0.0
        else:
            # Chi-Square adjustment for lower bound
            lower_lim = 0.5 * chi2.ppf(alpha_tail, 2 * dist_from_bottom) / n_eff

    # 3. Handle perfect compliance edge case (p_hat=1.0)
    if p_hat >= 1.0:
        upper_lim = 1.0
        # If it was 1.0, lower limit is handled by Wilson or Chi-Square above.

    return max(0.0, lower_lim), min(1.0, upper_lim), method_used

# Alias for backward compatibility if needed, but we update callers.
def wilson_score_upper_tolerance(*args, **kwargs):
    # This wrapper maintains the return signature of the old function if it was different,
    # or just forwards it.
    # The old signature return was likely just 'rank' or similar if it was 1-sided.
    # But based on memory/usage, it returns (lower, upper, method).
    # If the tests expect a single value (upper limit) for `wilson_score_upper_tolerance`,
    # we might need to adapt.
    # Checking `test_audit_fixes.py`:
    #   utl_rank_corr = wilson_score_upper_tolerance(...)
    # It expects a single float return value!

    # The new function returns a tuple (lower, upper, method).
    # We must adapt this alias to return just the Upper Limit (rank) for backward compatibility
    # with tests that treat it as a calculation function.

    res = wilson_score_interval(*args, **kwargs)
    return res[1] # Return upper_lim
