import numpy as np
import pandas as pd
import scipy.stats as stats
from whatts import calculate_tolerance_limit
from whatts.utils import project_to_current_state

n_samples = 200
slope = 0.05
target_percentile = 0.95

# Generate Data
np.random.seed(42)
noise = np.random.normal(0, 1, n_samples)
t = np.arange(n_samples)
data = t * slope + noise

# True Value at end
true_mean_at_end = (n_samples - 1) * slope
true_value = true_mean_at_end + stats.norm.ppf(target_percentile)
print(f"True Value at End: {true_value:.4f} (Mean: {true_mean_at_end:.4f})")

dates = pd.date_range(start='2020-01-01', periods=n_samples, freq='D')
df = pd.DataFrame({'value': data, 'date': dates})

# Check Projection manually
proj = project_to_current_state(dates, data, target_date='end')
print(f"Detected Slope (per year): {proj['slope_per_year']:.4f}")
print(f"Detected Slope (per step): {proj['slope_per_year'] / 365.25:.4f}")

# Projected data stats
p_data = proj['projected_data']
print(f"Projected Data Mean: {np.mean(p_data):.4f}")
print(f"Projected Data Std: {np.std(p_data):.4f}")

# Run whatts
res = calculate_tolerance_limit(
    df, 'date', 'value',
    target_percentile=target_percentile,
    method='projection',
    projection_target_date='end',
    sides=2
)

print("\n--- Results ---")
print(f"LTL: {res['lower_tolerance_limit']:.4f}")
print(f"UTL: {res['upper_tolerance_limit']:.4f}")
print(f"Point Est: {res['point_estimate']:.4f}")
print(f"N_eff: {res['n_eff']:.4f}")

if res['lower_tolerance_limit'] <= true_value <= res['upper_tolerance_limit']:
    print("PASS: True value inside interval")
else:
    print("FAIL: True value outside interval")
