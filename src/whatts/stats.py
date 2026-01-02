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

def calculate_neff_sum_corr(data):
    """
    Calculates Effective Sample Size (n_eff) using Sum of Correlations.
    (Unchanged from v1)
    """
    n = len(data)
    if n < 3: return float(n)

    y = data - np.mean(data)
    var = np.var(y)
    if var == 0: return float(n)

    sum_rho = 0.0
    for k in range(1, int(n / 2)):
        rho_k = np.sum(y[:-k] * y[k:]) / (n * var)
        if rho_k < 0: break
        sum_rho += rho_k * (1 - k/n)

    n_eff = n / (1 + 2 * sum_rho)
    return max(2.0, min(float(n), n_eff))

def wilson_score_upper_tolerance(p_hat, n, n_eff=None, conf_level=0.95):
    """
    Calculates the One-Sided Upper Wilson Limit (Non-Parametric Upper Tolerance Limit).

    Args:
        p_hat (float): The target percentile (e.g., 0.95).
        n (int): Raw sample size (for boundary corrections).
        n_eff (float): Effective sample size (for variance).
        conf_level (float): Confidence level (default 0.95).

    Returns:
        float: The probability rank corresponding to the Upper Tolerance Limit.
    """
    if n_eff is None:
        n_eff = n

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
    x = p_hat * n
    dist_from_top = n - x

    # Logic adapted from R 'binom.CI' but specific to Upper Limit
    is_small = (n <= 50 and dist_from_top <= 2)
    is_med = (51 <= n <= 100 and dist_from_top <= 3)

    if is_small or is_med:
        # One-sided Chi-Square adjustment for upper bound
        # The R code used alpha/2 implicitly for 2-sided.
        # For 1-sided, we use alpha directly.
        # Note: We use alpha directly as we are doing a one-sided test,
        # which is more stringent than the two-sided adjustment with alpha.
        upper_lim = 1.0 - 0.5 * chi2.ppf(alpha, 2 * dist_from_top) / n

    return min(1.0, upper_lim)
