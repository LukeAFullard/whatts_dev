import numpy as np
import pandas as pd
import MannKS
from datetime import datetime

# Synthetic data: y = 2*t
# t in days.
n = 100
slope_per_day = 2.0
t_days = np.arange(n)
values = slope_per_day * t_days
# Perfect line.

dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
date_seconds = dates.map(pd.Timestamp.timestamp).values

# Run MannKS
mk = MannKS.trend_test(values, date_seconds)
print(f"Slope (per second): {mk.slope}")
print(f"P-value: {mk.p}")

# Expected slope per second
seconds_per_day = 24 * 3600
expected_slope = slope_per_day / seconds_per_day
print(f"Expected Slope: {expected_slope}")

ratio = mk.slope / expected_slope
print(f"Ratio: {ratio}")
