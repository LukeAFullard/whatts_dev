import numpy as np
import pandas as pd
from scipy.stats import norm
from whatts.core import calculate_tolerance_limit
import warnings

# Suppress small sample size warnings for clean output
warnings.filterwarnings("ignore", category=UserWarning)

def run_validation():
    # Parameters
    N = 60
    ITERATIONS = 1000
    CONFIDENCE = 0.95

    # Percentiles to check
    # 50 to 90 in steps of 5
    p1 = list(range(50, 90, 5))
    # 90 to 99 in steps of 1
    p2 = list(range(90, 100, 1))

    percentiles = sorted(list(set(p1 + p2)))
    target_ps = [p / 100.0 for p in percentiles]

    print(f"Validation Parameters:")
    print(f"  N = {N}")
    print(f"  Iterations = {ITERATIONS}")
    print(f"  Confidence (Target Coverage) = {CONFIDENCE}")
    print(f"  Distribution = Standard Normal (mean=0, std=1)")
    print("-" * 65)
    print(f"{'Target %ile':<15} {'True Value':<15} {'Actual Coverage':<18} {'Status':<10}")
    print("-" * 65)

    # Pre-generate random data for consistency/speed (optional, but here we do it per loop)
    # Actually, generating per loop is better to ensure independence across P

    results = []

    np.random.seed(42)

    for p in target_ps:
        success_count = 0
        true_value = norm.ppf(p)

        for _ in range(ITERATIONS):
            # Generate Data (Standard Normal)
            values = np.random.normal(0, 1, N)
            dates = pd.date_range("2020-01-01", periods=N, freq="D")
            df = pd.DataFrame({"date": dates, "value": values})

            # Calculate UTL
            # WH only, no QR -> method='projection'
            # We use default use_projection=True, but data has no trend.
            try:
                res = calculate_tolerance_limit(
                    df, "date", "value",
                    target_percentile=p,
                    confidence=CONFIDENCE,
                    method="projection"
                )
                utl = res["upper_tolerance_limit"]

                if utl >= true_value:
                    success_count += 1
            except Exception as e:
                # Should not happen
                print(f"Error: {e}")

        coverage = success_count / ITERATIONS
        status = "PASS" if abs(coverage - CONFIDENCE) <= 0.03 else "FAIL"

        print(f"{p:<15.2f} {true_value:<15.4f} {coverage:<18.4f} {status:<10}")
        results.append((p, coverage))

    print("-" * 65)
    print("Done.")

if __name__ == "__main__":
    run_validation()
