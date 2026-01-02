from collections import namedtuple
import numpy as np
from scipy.stats import norm, mstats

MKResult = namedtuple('MKResult', ['trend', 'h', 'p_value', 'z', 'Tau', 's', 'var_s', 'slope', 'intercept'])

def mann_kendall(x, alpha=0.05):
    """
    Mann-Kendall Trend Test
    """
    n = len(x)

    # calculate S
    s = 0
    for k in range(n-1):
        for j in range(k+1, n):
            s += np.sign(x[j] - x[k])

    # calculate unique values
    unique_x, tp = np.unique(x, return_counts=True)
    g = len(unique_x)

    # calculate var(s)
    if n == g: # no ties
        var_s = (n*(n-1)*(2*n+5))/18
    else:
        var_s = (n*(n-1)*(2*n+5) - np.sum(tp*(tp-1)*(2*tp+5)))/18

    if s > 0:
        z = (s - 1)/np.sqrt(var_s)
    elif s < 0:
        z = (s + 1)/np.sqrt(var_s)
    else: # s == 0
        z = 0

    # calculate p_value
    p = 2*(1-norm.cdf(abs(z))) # two tail test
    h = abs(z) > norm.ppf(1-alpha/2)

    trend = 'no trend'
    if z > 0 and h:
        trend = 'increasing'
    elif z < 0 and h:
        trend = 'decreasing'

    return MKResult(trend, h, p, z, s, s, var_s, 0, 0) # simplified return

def sens_slope(x):
    """
    Sen's Slope Estimator
    """
    n = len(x)
    slopes = []
    for k in range(n-1):
        for j in range(k+1, n):
            slopes.append((x[j] - x[k]) / (j - k))

    return np.median(slopes)
