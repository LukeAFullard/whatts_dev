import sys
import os
import numpy as np
import pandas as pd
from scipy.stats import norm
import warnings
import time
from datetime import datetime

# Add project root to path
# Assuming script is in validation/cases/V-XX/script.py
# Root is ../../../
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))

try:
    from whatts.core import calculate_tolerance_limit
except ImportError:
    # Fallback/Debug
    print("Could not import whatts.core. Checking path...")
    print(sys.path)
    raise

# Suppress warnings
warnings.filterwarnings("ignore")

def run_test():
    # Parameters
    CASE_ID = "V-01e_p95_alpha01"
    N = 200
    PERCENTILE = 0.95
    METHOD_CODE = "QR"
    METHOD_NAME = "quantile_regression"
    ITERATIONS = 200
    CONFIDENCE = 0.90
    SIDES = 2

    # Target Coverage for UTL of a 2-sided 95% interval is 97.5%
    # because the interval [LTL, UTL] covers 95%, leaving 2.5% in each tail.
    # So UTL is the 97.5th percentile estimator.
    EXPECTED_COVERAGE = CONFIDENCE

    TRUE_VALUE = norm.ppf(PERCENTILE)

    log_file = os.path.join(os.path.dirname(__file__), f"log_{METHOD_CODE}_N{N}.txt")

    with open(log_file, "w") as f:
        f.write(f"Starting test {CASE_ID} - N={N}, Method={METHOD_NAME}\n")
        f.write(f"Target Percentile: {PERCENTILE}, True Value: {TRUE_VALUE:.4f}\n")
        f.write(f"Confidence: {CONFIDENCE}, Sides: {SIDES} -> Expected Interval Coverage: {EXPECTED_COVERAGE:.4f}\n")

    print(f"Running {CASE_ID} N={N} {METHOD_NAME}...")

    success_count = 0
    width_sum = 0.0
    start_time = time.time()

    # Seed based on parameters to ensure reproducibility but variation across cases
    # N is int, PERCENTILE is float.
    np.random.seed(42 + N + int(PERCENTILE*1000) + 1)

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
                method=METHOD_NAME,
                sides=SIDES
            )
            utl = res["upper_tolerance_limit"]
            ltl = res["lower_tolerance_limit"]
            width_sum += (utl - ltl)

            # Check coverage: Does the calculated UTL exceed the true percentile?
            if ltl <= TRUE_VALUE <= utl:
                success_count += 1

        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"Iteration {i+1} Error: {e}\n")

        # Logging progress
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            with open(log_file, "a") as f:
                f.write(f"Iteration {i+1}/{ITERATIONS} - Elapsed: {elapsed:.2f}s\n")
            # Don't print too much to stdout if running in batch

    coverage = success_count / ITERATIONS
    avg_width = width_sum / ITERATIONS
    # Success Criteria: Within 3% of Expected Coverage (0.975)
    status = "PASS" if abs(coverage - EXPECTED_COVERAGE) <= 0.03 else "FAIL"

    # Result entry
    # Columns: test_id,scenario,method,iterations,target_coverage,actual_coverage,avg_width,pass_status,timestamp
    result_line = [
        f"{CASE_ID}_p{int(PERCENTILE*100)}_N{N}", # test_id
        f"p{int(PERCENTILE*100)}_N{N}", # scenario
        METHOD_NAME, # method
        str(ITERATIONS), # iterations
        str(CONFIDENCE), # target_coverage (nominal)
        f"{coverage:.4f}", # actual_coverage
        f"{avg_width:.4f}", # avg_width
        status, # pass_status
        datetime.now().isoformat() # timestamp
    ]

    # Append to master results
    master_path = os.path.join(os.path.dirname(__file__), "../../master_results.csv")

    # Use simple file append. If parallel execution causes race conditions,
    # we might lose a line, but for this setup it is likely acceptable.
    # Ensure header exists
    if not os.path.exists(master_path):
        with open(master_path, "w") as f:
            f.write("test_id,scenario,method,iterations,target_coverage,actual_coverage,avg_width,pass_status,timestamp\n")

    with open(master_path, "a") as f:
        f.write(",".join(result_line) + "\n")

    with open(log_file, "a") as f:
        f.write(f"Finished. Coverage: {coverage:.4f} (Target: {EXPECTED_COVERAGE:.4f}), Status: {status}\n")
    print(f"Finished {CASE_ID} N={N} {METHOD_NAME}. Coverage: {coverage:.4f} - {status}")

if __name__ == "__main__":
    run_test()
