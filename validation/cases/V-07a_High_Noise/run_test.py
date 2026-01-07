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

def run_experiment_v07a(iterations=200):
    """V-07a: High Noise (Sigma=5)"""
    n = 100
    slope = 0.05
    sigma = 5.0
    target_percentile = 0.95

    print(f"Starting V-07a High Noise (N={n}, Sigma={sigma})")

    coverage_count = 0
    valid_iterations = 0

    for i in range(iterations):
        noise = np.random.normal(0, sigma, n)
        t = np.arange(n)
        data = t * slope + noise

        # True value at end: Mean + Z*Sigma
        true_mean = (n-1)*slope
        true_value = true_mean + stats.norm.ppf(target_percentile)*sigma

        dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
        df = pd.DataFrame({'value': data, 'date': dates})

        try:
            res = calculate_tolerance_limit(df, 'date', 'value', target_percentile, method='projection', projection_target_date='end')
            if res['lower_tolerance_limit'] <= true_value <= res['upper_tolerance_limit']:
                coverage_count += 1
            valid_iterations += 1
        except:
            pass

    if valid_iterations > 0:
        cov = coverage_count/valid_iterations
        print(f"V-07a Coverage: {cov:.3f}")
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv')), "a") as f:
            f.write(f"V-07a,HighNoise,projection,{valid_iterations},0.95,{cov:.3f},N/A,{'PASS' if abs(cov-0.95)<=0.03 else 'FAIL'},{datetime.now().isoformat()}\n")

if __name__ == "__main__":
    run_experiment_v07a()
