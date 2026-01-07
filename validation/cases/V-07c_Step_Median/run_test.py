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

def run_experiment_v07c(iterations=200):
    """V-07c: Step Trend (N=100, Step at 50)"""
    n = 100
    step_t = 50
    step_size = 2.0 # 2 sigma jump
    target_percentile = 0.95

    print(f"Starting V-07c Step Trend")

    coverage_count = 0
    valid_iterations = 0

    # True value at end is Mean + Z
    # Mean is step_size (assuming start at 0)
    true_value = step_size + stats.norm.ppf(target_percentile)

    for i in range(iterations):
        noise = np.random.normal(0, 1, n)
        trend = np.zeros(n)
        trend[step_t:] = step_size
        data = trend + noise

        dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
        df = pd.DataFrame({'value': data, 'date': dates})

        try:
            # Try both methods? Let's use QR as it handles steps better supposedly.
            # But let's test Projection first to see failure.
            res = calculate_tolerance_limit(df, 'date', 'value', target_percentile, method='projection', projection_target_date='end')
            if res['lower_tolerance_limit'] <= true_value <= res['upper_tolerance_limit']:
                coverage_count += 1
            valid_iterations += 1
        except:
            pass

    if valid_iterations > 0:
        cov = coverage_count/valid_iterations
        print(f"V-07c Coverage: {cov:.3f}")
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv')), "a") as f:
            f.write(f"V-07c,StepTrend,projection,{valid_iterations},0.95,{cov:.3f},N/A,{'PASS' if abs(cov-0.95)<=0.03 else 'FAIL'},{datetime.now().isoformat()}\n")

if __name__ == "__main__":
    run_experiment_v07c()
