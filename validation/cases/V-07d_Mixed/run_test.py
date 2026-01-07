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

def run_experiment_v07d(iterations=200):
    """V-07d: Mixed (Gamma + Linear Trend + Rho)"""
    n = 100
    rho = 0.5
    slope = 0.05
    shape = 2.0
    scale = 1.0 # Mean=2, Var=2
    # But for AR(1) with Gamma marginals is hard.
    # Instead, generate AR(1) Normal, then transform to Gamma?
    # Copula method.

    target_percentile = 0.95
    print(f"Starting V-07d Mixed")

    coverage_count = 0
    valid_iterations = 0

    # True value at end.
    # Mean trend is added to the Gamma variable? Or Gamma mean shifts?
    # Model: Y_t = Trend_t + Noise_t
    # Noise_t is Autocorrelated Gamma?
    # Let's say: Z_t is AR(1) Normal(0,1).
    # X_t = F_Gamma^-1( F_Norm(Z_t) ) -> This has Gamma marginals.
    # Y_t = Trend_t + X_t.

    # True Median/Percentile of Y_t at end:
    # Trend_end + Gamma_Percentile.

    true_gamma_p = stats.gamma.ppf(target_percentile, a=shape, scale=scale)
    trend_end = (n-1)*slope
    true_value = trend_end + true_gamma_p

    for i in range(iterations):
        # 1. Generate AR(1) Normal
        z = np.zeros(n)
        z[0] = np.random.normal(0, 1)
        noise_scale = np.sqrt(1 - rho**2)
        wn = np.random.normal(0, 1, n)
        for t in range(1, n):
            z[t] = rho * z[t-1] + noise_scale * wn[t]

        # 2. Transform to Gamma
        u = stats.norm.cdf(z)
        x = stats.gamma.ppf(u, a=shape, scale=scale)

        # 3. Add Trend
        t_arr = np.arange(n)
        y = t_arr * slope + x

        dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
        df = pd.DataFrame({'value': y, 'date': dates})

        try:
            res = calculate_tolerance_limit(df, 'date', 'value', target_percentile, method='projection', projection_target_date='end')
            if res['lower_tolerance_limit'] <= true_value <= res['upper_tolerance_limit']:
                coverage_count += 1
            valid_iterations += 1
        except:
            pass

    if valid_iterations > 0:
        cov = coverage_count/valid_iterations
        print(f"V-07d Coverage: {cov:.3f}")
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../master_results.csv')), "a") as f:
            f.write(f"V-07d,Mixed,projection,{valid_iterations},0.95,{cov:.3f},N/A,{'PASS' if abs(cov-0.95)<=0.03 else 'FAIL'},{datetime.now().isoformat()}\n")

if __name__ == "__main__":
    run_experiment_v07d()
