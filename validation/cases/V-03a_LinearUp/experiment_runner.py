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

def run_experiment(
    n_samples,
    method_name,
    trend_type, # 'linear_up', 'linear_down'
    slope_sigma_per_t, # Slope in units of sigma per time step
    target_percentile=0.95,
    iterations=200,
    n_boot=1000,
    output_csv=None
):
    """
    Runs the validation experiment for Trends.
    """

    if output_csv is None:
        output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv'))

    print(f"Starting {method_name} validation for {trend_type} (N={n_samples})")

    coverage_count = 0
    width_sum = 0
    valid_iterations = 0

    log_file = f"progress_log_N{n_samples}_{method_name}.txt"
    with open(log_file, "w") as f:
        f.write(f"Starting validation at {datetime.now()}\n")
        f.write(f"Params: N={n_samples}, Method={method_name}, Trend={trend_type}, Slope={slope_sigma_per_t}, Iterations={iterations}\n")

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
        # Standard Normal Noise
        noise = np.random.normal(0, 1, n_samples)

        # Trend
        # Slope is sigma per time step. Since sigma=1, it is value per time step.
        # We start at 0.
        t = np.arange(n_samples)
        trend_component = t * slope_sigma_per_t

        data = trend_component + noise

        # Calculate True Value at End of Series (Current State)
        # True Mean at t = N-1 (last point) is (N-1)*slope
        # True StdDev is 1.0
        # True Percentile = Mean + Z*StdDev
        z_score = stats.norm.ppf(target_percentile)
        true_mean_at_end = (n_samples - 1) * slope_sigma_per_t
        true_value = true_mean_at_end + z_score * 1.0

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
                n_boot=n_boot,
                projection_target_date='end' # IMPORTANT: Project to end to match true_value calculation
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

    scenario = f"{trend_type} (N={n_samples})"
    result_line = f"{test_id},{scenario},{method_name},{valid_iterations},{target_coverage},{actual_coverage:.3f},{avg_width:.3f},{status},{datetime.now().isoformat()}"

    with open(output_csv, "a") as f:
        f.write(result_line + "\n")

    with open(log_file, "a") as f:
        f.write(f"Completed at {datetime.now()}. Result: {result_line}\n")
