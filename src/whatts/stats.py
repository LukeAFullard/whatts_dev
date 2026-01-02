import numpy as np
from scipy.stats import norm, chi2

def hazen_plotting_position(n):
    """
    Generates the Hazen plotting positions for a sample size n.
    Formula: (i - 0.5) / n
    """
    return (np.arange(1, n + 1) - 0.5) / n

def hazen_interpolate(data, target_rank):
    """
    Interpolates a value from 'data' at the specific 'target_rank' (0 to 1)
    using the Hazen plotting position definition.
    """
    data_sorted = np.sort(data)
    n = len(data)

    # The 'x-axis' for interpolation
    hazen_ranks = hazen_plotting_position(n)

    # Use numpy linear interpolation
    # np.interp returns the value at the target rank
    return np.interp(target_rank, hazen_ranks, data_sorted)

def calculate_neff_sum_corr(data):
    """
    Calculates Effective Sample Size (n_eff) using the Bayley & Hammersley
    'Sum of Correlations' method.
    It truncates the sum when autocorrelation becomes negative.
    """
    n = len(data)
    if n < 3:
        return float(n)

    # Work with residuals from the mean
    y = data - np.mean(data)
    variance = np.var(y)

    if variance == 0:
        return float(n)

    # Calculate autocorrelation at lags k=1, 2, ...
    # We stop when correlation drops below zero (common heuristic for environmental data)
    # or if we reach n/2 lags.

    sum_rho = 0.0

    for k in range(1, int(n / 2)):
        # Calculate lag-k correlation
        # cov(y_t, y_{t+k}) / var(y)
        rho_k = np.sum(y[:-k] * y[k:]) / (n * variance)

        if rho_k < 0:
            break

        # Apply the weighting factor (1 - k/n) from Bayley & Hammersley
        sum_rho += rho_k * (1 - k/n)

    # Formula: 1/neff = 1/n * (1 + 2 * sum_weighted_rho)
    # n/neff = 1 + 2 * sum
    # neff = n / (1 + 2 * sum)

    correction_factor = 1 + 2 * sum_rho
    n_eff = n / correction_factor

    # Clamp n_eff. It cannot be less than 2 (statistically unstable)
    # and cannot be more than n (unless negative correlation exists,
    # but we clamped rho at 0).
    return max(2.0, min(float(n), n_eff))

def wilson_score_interval_corrected(p_hat, n, n_eff=None, alpha=0.05):
    """
    Calculates the Wilson Score Interval with Chi-Square boundary corrections.
    Direct port of R function 'binom.CI'.

    Args:
        p_hat (float): The target proportion (e.g., 0.95).
        n (int): The raw sample size (used for boundary logic).
        n_eff (float): The effective sample size (used for variance calculation).
        alpha (float): Significance level (default 0.05 for 95% CI).

    Returns:
        tuple: (lower_probability, upper_probability)
    """
    if n_eff is None:
        n_eff = n

    # Critical values
    z_alpha = norm.ppf(1 - (alpha / 2))
    z_alpha_low = norm.ppf(alpha / 2) # Negative of z_alpha

    # --- Standard Wilson Calculation (using n_eff) ---
    denom = 1 + (z_alpha**2 / n_eff)
    center = (p_hat + (z_alpha**2 / (2 * n_eff)))

    term_inside_sqrt = (p_hat * (1 - p_hat) / n_eff) + (z_alpha**2 / (4 * n_eff**2))
    # Safety clamp for negative variance due to floating point
    term_inside_sqrt = max(0.0, term_inside_sqrt)

    error_margin = np.sqrt(term_inside_sqrt)

    upper_lim = (center + z_alpha * error_margin) / denom
    lower_lim = (center + z_alpha_low * error_margin) / denom

    # --- Boundary Corrections (The R Logic) ---
    # x represents the number of 'successes' implies by the proportion
    x = p_hat * n

    # R Code logic translation:
    # if ((n <= 50 & x %in% c(1, 2)) | (n >= 51 & n <= 100 & x %in% c(1:3)))

    # Note: We use rough integer comparison for 'x' to match R's discrete logic
    # even though percentiles are continuous.

    # Lower Boundary Correction (Values close to 0)
    if (n <= 50 and x <= 2) or (51 <= n <= 100 and x <= 3):
        # R: lower.lim <- 0.5 * qchisq(alpha, 2 * x)/n
        # Python:
        lower_lim = 0.5 * chi2.ppf(alpha, 2 * x) / n

    # Upper Boundary Correction (Values close to 1)
    # x is close to n. (n-x) is small.
    dist_from_top = n - x

    if (n <= 50 and dist_from_top <= 2) or (51 <= n <= 100 and dist_from_top <= 3):
        # R: upper.lim <- 1 - 0.5 * qchisq(alpha, 2 * (n - x))/n
        # Python:
        upper_lim = 1.0 - 0.5 * chi2.ppf(alpha, 2 * dist_from_top) / n

    # Final clamps to valid probability range
    return max(0.0, lower_lim), min(1.0, upper_lim)
