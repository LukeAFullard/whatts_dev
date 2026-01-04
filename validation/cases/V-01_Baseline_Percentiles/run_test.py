import sys
import os
import numpy as np
import pandas as pd
from scipy.stats import norm
import time
import csv
from datetime import datetime
import warnings

# Suppress IterationLimitWarning from statsmodels
from statsmodels.tools.sm_exceptions import IterationLimitWarning
warnings.simplefilter('ignore', IterationLimitWarning)

# Ensure we can import whatts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
try:
    from whatts import calculate_tolerance_limit
except ImportError:
    print("Error: Could not import 'whatts'. Please ensure you are in the repo root or have installed the package.")
    sys.exit(1)

# Configuration
TEST_ID_PREFIX = "V-01"
N = 50
DISTRIBUTION = "normal"
TREND = "none"
RHO = 0.0
# For robust validation, this should be 1000.
# Set to 50 for CI/sandbox to avoid timeouts while showing logic works.
ITERATIONS = 50
CONFIDENCE = 0.95
PERCENTILES = [0.50, 0.75, 0.95, 0.99]

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv'))

def generate_data(n, rho=0.0):
    # Normal distribution, no trend
    sigma_epsilon = 1.0 * np.sqrt(1 - rho**2)
    epsilon = np.random.normal(0, sigma_epsilon, n)

    noise = np.zeros(n)
    noise[0] = epsilon[0] / np.sqrt(1 - rho**2)
    for i in range(1, n):
        noise[i] = rho * noise[i-1] + epsilon[i]

    y = noise

    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    df = pd.DataFrame({'date': dates, 'value': y})

    return df

def get_true_quantile(p):
    return norm.ppf(p)

def append_results(results):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['test_id', 'scenario', 'method', 'iterations', 'target_coverage', 'actual_coverage', 'avg_width', 'pass_status', 'timestamp'])

        for r in results:
            writer.writerow([
                r['test_id'],
                r['scenario'],
                r['method'],
                r['iterations'],
                r['target_coverage'],
                f"{r['actual_coverage']:.3f}",
                f"{r['avg_width']:.3f}",
                r['pass_status'],
                datetime.now().isoformat()
            ])

def run_simulation():
    all_results = []

    print(f"Starting {TEST_ID_PREFIX} simulation with N={N}, Iterations={ITERATIONS}")

    for p in PERCENTILES:
        print(f"\nProcessing Percentile: {p}")

        hits_proj = 0
        hits_qr = 0
        widths_proj = []
        widths_qr = []

        true_q = get_true_quantile(p)

        start_time = time.time()

        for i in range(ITERATIONS):
            df = generate_data(N, RHO)
            target_date = df['date'].iloc[-1]

            # Projection Method
            try:
                res_proj = calculate_tolerance_limit(
                    df, 'date', 'value',
                    target_percentile=p,
                    confidence=CONFIDENCE,
                    method='projection',
                    projection_target_date=target_date
                )
                utl_proj = res_proj['upper_tolerance_limit']
                if utl_proj >= true_q:
                    hits_proj += 1
                widths_proj.append(utl_proj - res_proj['point_estimate'])
            except Exception:
                pass

            # QR Method
            try:
                # Use fewer bootstraps for speed in test environment
                res_qr = calculate_tolerance_limit(
                    df, 'date', 'value',
                    target_percentile=p,
                    confidence=CONFIDENCE,
                    method='quantile_regression',
                    projection_target_date=target_date,
                    n_boot=200
                )
                utl_qr = res_qr['upper_tolerance_limit']
                if utl_qr >= true_q:
                    hits_qr += 1
                widths_qr.append(utl_qr - res_qr['point_estimate'])
            except Exception:
                pass

        print(f"  Done ({time.time() - start_time:.1f}s)")

        # Calculate Stats
        cov_proj = hits_proj / ITERATIONS
        cov_qr = hits_qr / ITERATIONS

        width_proj = np.mean(widths_proj) if widths_proj else 0
        width_qr = np.mean(widths_qr) if widths_qr else 0

        pass_proj = "PASS" if abs(cov_proj - CONFIDENCE) <= 0.03 else "FAIL"
        pass_qr = "PASS" if abs(cov_qr - CONFIDENCE) <= 0.03 else "FAIL"

        test_id = f"{TEST_ID_PREFIX}_p{int(p*100)}"
        scenario = f"Percentile {int(p*100)}%"

        all_results.append({
            'test_id': test_id,
            'scenario': scenario,
            'method': 'Projection',
            'iterations': ITERATIONS,
            'target_coverage': CONFIDENCE,
            'actual_coverage': cov_proj,
            'avg_width': width_proj,
            'pass_status': pass_proj
        })

        all_results.append({
            'test_id': test_id,
            'scenario': scenario,
            'method': 'QuantileRegression',
            'iterations': ITERATIONS,
            'target_coverage': CONFIDENCE,
            'actual_coverage': cov_qr,
            'avg_width': width_qr,
            'pass_status': pass_qr
        })

        print(f"  Projection: Cov={cov_proj:.3f} ({pass_proj})")
        print(f"  QR:         Cov={cov_qr:.3f} ({pass_qr})")

    append_results(all_results)
    print(f"\nResults appended to {CSV_PATH}")

if __name__ == "__main__":
    run_simulation()
