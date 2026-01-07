import sys
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import time
from datetime import datetime

# Add source to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

try:
    from whatts import calculate_tolerance_limit
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))
    from whatts import calculate_tolerance_limit

def generate_ar1_data(n, rho, sigma=1.0):
    """Generates AR(1) data: x_t = rho * x_{t-1} + epsilon_t"""
    data = np.zeros(n)
    # Start with random value from stationary distribution
    # Variance of AR(1) is sigma^2 / (1 - rho^2)
    # So if we want process variance 1.0, epsilon should be scaled.
    # But usually we just generate and let variance be what it is, then normalize?
    # Or just generate:
    # x_0 ~ N(0, 1)
    # x_t = rho * x_{t-1} + sqrt(1-rho^2)*N(0,1) -> This maintains variance 1.0.

    data[0] = np.random.normal(0, 1)
    noise_scale = np.sqrt(1 - rho**2)
    noise = np.random.normal(0, 1, n)

    for t in range(1, n):
        data[t] = rho * data[t-1] + noise_scale * noise[t]

    return data

def run_experiment(
    n_samples,
    method_name,
    rho,
    target_percentile=0.95,
    iterations=200,
    n_boot=1000,
    output_csv=None
):
    """
    Runs the validation experiment for Autocorrelation.
    """

    if output_csv is None:
        output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv'))

    print(f"Starting {method_name} validation for AR(1) rho={rho} (N={n_samples})")

    coverage_count = 0
    width_sum = 0
    valid_iterations = 0

    log_file = f"progress_log_N{n_samples}_{method_name}.txt"
    with open(log_file, "w") as f:
        f.write(f"Starting validation at {datetime.now()}\n")
        f.write(f"Params: N={n_samples}, Method={method_name}, Rho={rho}, Iterations={iterations}\n")

    start_time = time.time()

    # True value for N(0,1) since we maintain unit variance
    true_value = stats.norm.ppf(target_percentile)

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
        data = generate_ar1_data(n_samples, rho)

        # Create DataFrame
        dates = pd.date_range(start='2020-01-01', periods=n_samples, freq='D')
        df = pd.DataFrame({'value': data, 'date': dates})

        try:
            result = calculate_tolerance_limit(
                df,
                value_col='value',
                date_col='date',
                target_percentile=target_percentile,
                confidence=0.95,
                method=method_name,
                sides=2,
                n_boot=n_boot
            )

            utl = result['upper_tolerance_limit']
            ltl = result['lower_tolerance_limit']

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
    target_coverage = 0.95

    diff = abs(actual_coverage - target_coverage)
    status = "PASS" if diff <= 0.03 else "FAIL"

    print(f"Finished. Coverage: {actual_coverage:.3f}, Avg Width: {avg_width:.3f}, Status: {status}")

    folder_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    test_id = folder_name.split('_')[0]

    scenario = f"AR(1) rho={rho} (N={n_samples})"
    result_line = f"{test_id},{scenario},{method_name},{valid_iterations},{target_coverage},{actual_coverage:.3f},{avg_width:.3f},{status},{datetime.now().isoformat()}"

    with open(output_csv, "a") as f:
        f.write(result_line + "\n")

    with open(log_file, "a") as f:
        f.write(f"Completed at {datetime.now()}. Result: {result_line}\n")
