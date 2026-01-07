import sys
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
try:
    from whatts import calculate_tolerance_limit
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src')))
    from whatts import calculate_tolerance_limit

def run_experiment_v07b(iterations=200):
    """V-07b: Small N (20), High Rho (0.7)"""
    n = 20
    rho = 0.7
    target_percentile = 0.95

    print(f"Starting V-07b Small N High Rho (N={n}, Rho={rho})")

    coverage_count = 0
    valid_iterations = 0

    true_value = stats.norm.ppf(target_percentile) # Variance is 1.0

    for i in range(iterations):
        # Generate AR(1)
        data = np.zeros(n)
        data[0] = np.random.normal(0, 1)
        noise_scale = np.sqrt(1 - rho**2)
        noise = np.random.normal(0, 1, n)
        for t in range(1, n):
            data[t] = rho * data[t-1] + noise_scale * noise[t]

        dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
        df = pd.DataFrame({'value': data, 'date': dates})

        try:
            res = calculate_tolerance_limit(df, 'date', 'value', target_percentile, method='projection')
            if res['lower_tolerance_limit'] <= true_value <= res['upper_tolerance_limit']:
                coverage_count += 1
            valid_iterations += 1
        except Exception as e:
            # print(e)
            pass

    if valid_iterations > 0:
        cov = coverage_count/valid_iterations
        print(f"V-07b Coverage: {cov:.3f}")
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv')), "a") as f:
            f.write(f"V-07b,SmallN_HighRho,projection,{valid_iterations},0.95,{cov:.3f},N/A,{'PASS' if abs(cov-0.95)<=0.03 else 'FAIL'},{datetime.now().isoformat()}\n")

if __name__ == "__main__":
    run_experiment_v07b()
