import sys
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import time
from datetime import datetime

# Add source to path
# Assuming this file is in validation/cases/V-XX/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

try:
    from whatts.api import calculate_tolerance_limit
except ImportError:
    # Fallback if the path is slightly different or running from elsewhere
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))
    from whatts.api import calculate_tolerance_limit

def run_experiment(
    n_samples,
    method_name,
    dist_name,
    dist_params,
    target_percentile=0.95,
    iterations=200,
    n_boot=1000,
    output_csv=None
):
    """
    Runs the validation experiment.

    Args:
        n_samples (int): Sample size N.
        method_name (str): 'projection' or 'quantile_regression'.
        dist_name (str): 'lognormal', 'gamma', or 'uniform'.
        dist_params (dict): Parameters for the distribution.
        target_percentile (float): Target percentile (e.g., 0.95).
        iterations (int): Number of Monte Carlo iterations.
        n_boot (int): Bootstrap iterations for QR.
        output_csv (str): Path to master results file. Defaults to ../../master_results.csv
    """

    if output_csv is None:
        output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv'))

    # Calculate true percentile
    if dist_name == 'lognormal':
        # np.random.lognormal(mean, sigma) -> ln(X) ~ N(mean, sigma)
        # scipy.stats.lognorm takes shape=sigma, scale=exp(mean)
        sigma = dist_params['sigma']
        mean = dist_params['mean']
        true_value = stats.lognorm.ppf(target_percentile, s=sigma, scale=np.exp(mean))

    elif dist_name == 'gamma':
        # np.random.gamma(shape, scale)
        # scipy stats gamma: a=shape, scale=scale
        shape = dist_params['shape']
        scale = dist_params['scale']
        true_value = stats.gamma.ppf(target_percentile, a=shape, scale=scale)

    elif dist_name == 'uniform':
        low = dist_params['low']
        high = dist_params['high']
        true_value = stats.uniform.ppf(target_percentile, loc=low, scale=high-low)
    else:
        raise ValueError(f"Unknown distribution: {dist_name}")

    print(f"Starting {method_name} validation for {dist_name} (N={n_samples})")
    print(f"Target Percentile ({target_percentile}): {true_value:.4f}")

    coverage_count = 0
    width_sum = 0
    valid_iterations = 0

    log_file = f"progress_log_N{n_samples}_{method_name}.txt"
    with open(log_file, "w") as f:
        f.write(f"Starting validation at {datetime.now()}\n")
        f.write(f"Params: N={n_samples}, Method={method_name}, Dist={dist_name}, Iterations={iterations}\n")

    start_time = time.time()

    for i in range(iterations):
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / (i + 1)
            remaining = avg_time * (iterations - (i + 1))
            msg = f"Iteration {i+1}/{iterations}. Elapsed: {elapsed:.1f}s. Est remaining: {remaining:.1f}s"
            print(msg)
            with open(log_file, "a") as f:
                f.write(msg + "\n")

        # Generate Data
        if dist_name == 'lognormal':
            data = np.random.lognormal(dist_params['mean'], dist_params['sigma'], n_samples)
        elif dist_name == 'gamma':
            data = np.random.gamma(dist_params['shape'], dist_params['scale'], n_samples)
        elif dist_name == 'uniform':
            data = np.random.uniform(dist_params['low'], dist_params['high'], n_samples)

        # Create DataFrame with time index (required by whatts)
        dates = pd.date_range(start='2020-01-01', periods=n_samples, freq='D')
        df = pd.DataFrame({'value': data, 'date': dates})

        try:
            result = calculate_tolerance_limit(
                df,
                target_col='value',
                date_col='date',
                target_percentile=target_percentile,
                confidence_level=0.95, # Fixed to 95% confidence
                method=method_name,
                sides=2, # Always 2-sided
                n_boot=n_boot
            )

            utl = result['upper_tolerance_limit']
            ltl = result['lower_tolerance_limit']

            # Check coverage (Is true value between LTL and UTL?)
            # For 2-sided interval, coverage is P(LTL < True < UTL)
            # Note: calculate_tolerance_limit(target_percentile=P, sides=2) returns a Confidence Interval for the P-th percentile.
            # It does NOT return a population Tolerance Interval covering P% of the population (which would be centered at median).
            # Therefore, checking if the true P-th percentile is within [LTL, UTL] is the correct validation.
            if ltl <= true_value <= utl:
                coverage_count += 1

            width_sum += (utl - ltl)
            valid_iterations += 1

        except Exception as e:
            msg = f"Error in iteration {i}: {e}"
            print(msg)
            with open(log_file, "a") as f:
                f.write(msg + "\n")

    if valid_iterations == 0:
        print("No valid iterations.")
        return

    actual_coverage = coverage_count / valid_iterations
    avg_width = width_sum / valid_iterations

    target_coverage = 0.95 # Since we are checking if true value is in the 95% Confidence Interval

    diff = abs(actual_coverage - target_coverage)
    status = "PASS" if diff <= 0.03 else "FAIL"

    print(f"Finished. Coverage: {actual_coverage:.3f}, Avg Width: {avg_width:.3f}, Status: {status}")

    # Append to master results
    # Columns: test_id, scenario, method, iterations, target_coverage, actual_coverage, avg_width, pass_status, timestamp

    # Determine test_id based on folder name
    folder_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    test_id = folder_name.split('_')[0] # e.g. V-02a

    scenario = f"{dist_name.capitalize()} (N={n_samples})"

    result_line = f"{test_id},{scenario},{method_name},{valid_iterations},{target_coverage},{actual_coverage:.3f},{avg_width:.3f},{status},{datetime.now().isoformat()}"

    with open(output_csv, "a") as f:
        f.write(result_line + "\n")

    with open(log_file, "a") as f:
        f.write(f"Completed at {datetime.now()}. Result: {result_line}\n")
