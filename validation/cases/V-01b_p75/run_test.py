import sys
import os
import numpy as np
import pandas as pd
from scipy.stats import norm
import warnings
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))

try:
    from whatts.core import calculate_tolerance_limit
except ImportError:
    print("Could not import whatts.core. Checking path...")
    print(sys.path)
    raise

# Suppress warnings
warnings.filterwarnings("ignore")

def run_test():
    # Parameters for V-01b
    CASE_ID = "V-01b"
    SCENARIO_BASE = "p75"
    SAMPLE_SIZES = [30, 60, 100, 200]
    PERCENTILE = 0.75
    ITERATIONS = 200
    CONFIDENCE = 0.95
    SIDES = 2

    # Target Coverage for a 2-sided 95% interval is 95%
    # We check if the interval [LTL, UTL] contains the true value.
    EXPECTED_COVERAGE = CONFIDENCE
    TRUE_VALUE = norm.ppf(PERCENTILE)

    log_file = os.path.join(os.path.dirname(__file__), "progress_log.txt")

    # Initialize log
    with open(log_file, "w") as f:
        f.write(f"Starting Validation {CASE_ID}_{SCENARIO_BASE} - Full Sample Size Suite\n")
        f.write(f"Sample Sizes: {SAMPLE_SIZES}\n")
        f.write(f"Percentile={PERCENTILE}, Iterations={ITERATIONS}\n")
        f.write(f"True 75th Percentile: {TRUE_VALUE:.4f}\n")
        f.write(f"Target Interval Coverage: {EXPECTED_COVERAGE}\n")
        f.write("--------------------------------------------------\n")

    methods = [
        ("Projection", "projection"),
        ("Quantile Regression", "quantile_regression")
    ]

    master_results_lines = []

    for N in SAMPLE_SIZES:
        for pretty_name, method_name in methods:
            print(f"Running N={N} {pretty_name}...")
            with open(log_file, "a") as f:
                f.write(f"Starting N={N}, Method: {pretty_name} ({method_name})\n")

            success_count = 0
            width_sum = 0.0
            start_time = time.time()

            # Seed for reproducibility
            np.random.seed(42 + N + int(PERCENTILE*1000) + len(method_name))

            for i in range(ITERATIONS):
                # Generate Data (Standard Normal)
                values = np.random.normal(0, 1, N)
                dates = pd.date_range("2020-01-01", periods=N, freq="D")
                df = pd.DataFrame({"date": dates, "value": values})

                try:
                    res = calculate_tolerance_limit(
                        df, "date", "value",
                        target_percentile=PERCENTILE,
                        confidence=CONFIDENCE,
                        method=method_name,
                        sides=SIDES,
                        n_boot=200 # Reduced bootstrap iterations for speed if QR
                    )
                    utl = res["upper_tolerance_limit"]
                    ltl = res["lower_tolerance_limit"]
                    width_sum += (utl - ltl)

                    # Check Interval Coverage: Does the interval contain the true percentile?
                    if ltl <= TRUE_VALUE <= utl:
                        success_count += 1

                except Exception as e:
                    with open(log_file, "a") as f:
                        f.write(f"Iteration {i+1} Error: {e}\n")

                # Log progress every 20 iterations to reduce IO
                if (i + 1) % 20 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i + 1)
                    remaining = avg_time * (ITERATIONS - (i + 1))
                    with open(log_file, "a") as f:
                        f.write(f"[N={N} {pretty_name}] Iteration {i+1}/{ITERATIONS} - Elapsed: {elapsed:.2f}s, Remaining: ~{remaining:.1f}s\n")

            coverage = success_count / ITERATIONS
            avg_width = width_sum / ITERATIONS

            # Success Criteria
            status = "PASS" if abs(coverage - EXPECTED_COVERAGE) <= 0.03 else "FAIL"

            with open(log_file, "a") as f:
                f.write(f"Completed N={N} {pretty_name}. Coverage: {coverage:.4f} (Target: {EXPECTED_COVERAGE:.4f}), Status: {status}\n")
                f.write("--------------------------------------------------\n")

            # Prepare result line
            result_line = [
                f"{CASE_ID}_{SCENARIO_BASE}_N{N}",
                f"{SCENARIO_BASE}_N{N}",
                pretty_name,
                str(ITERATIONS),
                str(CONFIDENCE),
                f"{coverage:.4f}",
                f"{avg_width:.4f}",
                status,
                datetime.now().isoformat()
            ]
            master_results_lines.append(result_line)

            # Append to master results immediately to save progress
            master_path = os.path.join(os.path.dirname(__file__), "../../master_results.csv")
            if not os.path.exists(master_path):
                with open(master_path, "w") as f:
                    f.write("test_id,scenario,method,iterations,target_coverage,actual_coverage,avg_width,pass_status,timestamp\n")

            with open(master_path, "a") as f:
                f.write(",".join(result_line) + "\n")

    print("Test Suite Complete. Check progress_log.txt and master_results.csv")

if __name__ == "__main__":
    run_test()
