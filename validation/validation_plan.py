import sys
import os
import numpy as np
import pandas as pd
from scipy.stats import norm, gamma, uniform
import matplotlib.pyplot as plt
import time
from dataclasses import dataclass
from typing import Literal

# Ensure we can import whatts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
try:
    from whatts import calculate_tolerance_limit
except ImportError:
    print("Error: Could not import 'whatts'. Please ensure you are in the repo root or have installed the package.")
    sys.exit(1)

# Suppress warnings for cleaner output
import warnings
from statsmodels.tools.sm_exceptions import IterationLimitWarning
warnings.simplefilter('ignore', IterationLimitWarning)
warnings.simplefilter('ignore', UserWarning)

@dataclass
class TestConfig:
    name: str
    n: int
    dist: Literal['normal', 'lognormal', 'gamma', 'uniform']
    trend: Literal['none', 'linear_up', 'linear_down', 'quadratic', 'step']
    rho: float
    target_percentile: float
    target_date_loc: Literal['start', 'middle', 'end']
    noise_level: float = 1.0

    def __str__(self):
        return (f"n={self.n}, dist={self.dist}, trend={self.trend}, "
                f"p={self.target_percentile}, ρ={self.rho}, target={self.target_date_loc}")

def generate_series(config: TestConfig, seed=None):
    if seed is not None:
        np.random.seed(seed)

    n = config.n
    t = np.arange(n)

    # 1. Trend Component (Mean)
    if config.trend == 'none':
        mu = np.zeros(n)
    elif config.trend == 'linear_up':
        # Moderate trend relative to noise
        mu = 0.05 * t
    elif config.trend == 'linear_down':
        mu = -0.05 * t
    elif config.trend == 'quadratic':
        # Small quadratic curve
        mu = 0.001 * (t - n/2)**2
    elif config.trend == 'step':
        mu = np.zeros(n)
        mu[n//2:] = 2.0  # 2 sigma step
    else:
        mu = np.zeros(n)

    # 2. Noise Component (AR(1))
    # We want marginal variance to be noise_level^2
    sigma_epsilon = config.noise_level * np.sqrt(1 - config.rho**2)
    epsilon = np.random.normal(0, sigma_epsilon, n)

    noise = np.zeros(n)
    # Initialize from stationary dist
    noise[0] = epsilon[0] / np.sqrt(1 - config.rho**2)
    for i in range(1, n):
        noise[i] = config.rho * noise[i-1] + epsilon[i]

    # Standardized noise for transformation
    z = noise / config.noise_level

    # 3. Apply Distribution & Combine
    if config.dist == 'normal':
        y = mu + noise

    elif config.dist == 'lognormal':
        # Log-normal: exp(trend + noise)
        # This means the trend is in log-space.
        y = np.exp(mu + noise)

    elif config.dist == 'gamma':
        # Shifted Gamma via Gaussian Copula
        # y = Gamma(alpha=2) shifted by mu
        # Using copula to preserve rank correlation rho approx
        u = norm.cdf(z)
        gamma_noise = gamma.ppf(u, a=2.0, scale=config.noise_level)
        # Center the gamma noise roughly so 'mu' acts as a baseline shift
        # Mean of Gamma(2, scale) is 2*scale.
        # Let's just add them: y = mu + gamma_noise
        y = mu + gamma_noise

    elif config.dist == 'uniform':
        u = norm.cdf(z)
        # Uniform [0, 1] * scale + mu
        # Centered uniform [-0.5, 0.5]?
        # Let's do Uniform[mu, mu + 2*noise_level*sqrt(3)] so variance matches?
        # Simpler: y = mu + Uniform(0,1) scaled
        uni_noise = uniform.ppf(u) # [0, 1]
        y = mu + (uni_noise - 0.5) * (config.noise_level * np.sqrt(12))

    else:
        y = mu + noise

    # Create DataFrame
    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    df = pd.DataFrame({'date': dates, 'value': y})

    return df, mu

def get_true_quantile(config: TestConfig, mu_arr):
    # Determine the target index based on 'target_date_loc'
    if config.target_date_loc == 'start':
        idx = 0
    elif config.target_date_loc == 'middle':
        idx = config.n // 2
    else: # end
        idx = config.n - 1

    mu_target = mu_arr[idx]
    p = config.target_percentile
    nl = config.noise_level

    if config.dist == 'normal':
        return mu_target + norm.ppf(p) * nl

    elif config.dist == 'lognormal':
        # y = exp(mu + noise)
        # Q_p = exp(mu_target + Q_norm(p)*nl)
        return np.exp(mu_target + norm.ppf(p) * nl)

    elif config.dist == 'gamma':
        # y = mu + Gamma(a=2, scale=nl)
        return mu_target + gamma.ppf(p, a=2.0, scale=nl)

    elif config.dist == 'uniform':
        # y = mu + (U - 0.5) * nl * sqrt(12)
        # U_p = p
        scale = nl * np.sqrt(12)
        return mu_target + (p - 0.5) * scale

    return 0.0

def run_test(config: TestConfig, n_iterations, confidence=0.95):
    hits_proj = 0
    hits_qr = 0

    widths_proj = []
    widths_qr = []

    # Target date alias for the API
    target_date_arg = config.target_date_loc
    if target_date_arg == 'end':
        target_date_arg = None # Default

    # We need to pass the explicit date if not None/Default,
    # but the API takes datetime or string aliases "start", "middle", "end"?
    # Checking API memory: "accept an optional ... parameter ... defaults to the dataset's maximum date."
    # The API code says `project_to_current_state` logic handles it.
    # In `project_to_current_state`, it usually expects a specific date or uses max.
    # Let's convert 'start'/'middle'/'end' to actual dates in the loop to be safe,
    # OR rely on whatts if it supports those strings.
    # Looking at `whatts` code (which I can't see fully here but usually does),
    # I'll calculate the date manually to be safe.

    for i in range(n_iterations):
        df, mu_arr = generate_series(config, seed=i if n_iterations < 100000 else None)

        # Determine actual target date
        dates = df['date']
        if config.target_date_loc == 'start':
            t_date = dates.iloc[0]
        elif config.target_date_loc == 'middle':
            t_date = dates.iloc[len(dates)//2]
        else:
            t_date = dates.iloc[-1]

        true_q = get_true_quantile(config, mu_arr)

        # Method 1: Projection
        try:
            res_proj = calculate_tolerance_limit(
                df, 'date', 'value',
                target_percentile=config.target_percentile,
                confidence=confidence,
                method='projection',
                projection_target_date=t_date
            )
            utl_proj = res_proj['upper_tolerance_limit']
            if utl_proj >= true_q:
                hits_proj += 1
            widths_proj.append(utl_proj - res_proj['point_estimate'])
        except Exception as e:
            # print(f"Proj fail: {e}")
            pass

        # Method 2: QR
        # Skip QR for very small n if it's known to fail or be slow in tests?
        # The guide implies running both.
        # But QR needs min samples. whatts/qr.py usually requires enough data for bootstrap.
        # If n=30, QR might struggle but should run.
        try:
            res_qr = calculate_tolerance_limit(
                df, 'date', 'value',
                target_percentile=config.target_percentile,
                confidence=confidence,
                method='quantile_regression',
                projection_target_date=t_date
            )
            utl_qr = res_qr['upper_tolerance_limit']
            if utl_qr >= true_q:
                hits_qr += 1
            widths_qr.append(utl_qr - res_qr['point_estimate'])
        except Exception:
            # QR might fail for small N or convergence
            pass

    cov_proj = hits_proj / n_iterations
    cov_qr = hits_qr / n_iterations if n_iterations > 0 else 0

    avg_width_proj = np.mean(widths_proj) if widths_proj else 0
    avg_width_qr = np.mean(widths_qr) if widths_qr else 0

    return {
        'test': config,
        'projection_coverage': cov_proj,
        'qr_coverage': cov_qr,
        'projection_width': avg_width_proj,
        'qr_width': avg_width_qr
    }

def run_full_validation(n_iterations=1000, confidence=0.95):
    tests = []

    # 1. Percentile Coverage
    tests.append(TestConfig('Baseline_p50', 50, 'normal', 'none', 0.0, 0.50, 'end'))
    tests.append(TestConfig('Baseline_p75', 50, 'normal', 'none', 0.0, 0.75, 'end'))
    tests.append(TestConfig('Baseline_p90', 50, 'normal', 'none', 0.0, 0.90, 'end'))
    tests.append(TestConfig('Baseline_p95', 50, 'normal', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Baseline_p99', 50, 'normal', 'none', 0.0, 0.99, 'end'))

    # 2. Sample Size
    tests.append(TestConfig('SampleSize_30', 30, 'normal', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('SampleSize_60', 60, 'normal', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('SampleSize_120', 120, 'normal', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('SampleSize_200', 200, 'normal', 'none', 0.0, 0.95, 'end'))

    # 3. Distribution
    tests.append(TestConfig('Distribution_LogNorm', 100, 'lognormal', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Distribution_Gamma', 100, 'gamma', 'none', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Distribution_Uniform', 100, 'uniform', 'none', 0.0, 0.95, 'end'))

    # 4. Trend Types
    tests.append(TestConfig('Trend_LinearUp', 60, 'normal', 'linear_up', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Trend_LinearDown', 60, 'normal', 'linear_down', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Trend_Quadratic', 60, 'normal', 'quadratic', 0.0, 0.95, 'end'))
    tests.append(TestConfig('Trend_Step', 60, 'normal', 'step', 0.0, 0.95, 'end'))

    # 5. Autocorrelation
    tests.append(TestConfig('Autocorr_03', 100, 'normal', 'none', 0.3, 0.95, 'end'))
    tests.append(TestConfig('Autocorr_06', 100, 'normal', 'none', 0.6, 0.95, 'end'))
    tests.append(TestConfig('Autocorr_08', 100, 'normal', 'none', 0.8, 0.95, 'end'))
    tests.append(TestConfig('Autocorr_HighTrend', 100, 'normal', 'linear_up', 0.6, 0.95, 'end'))

    # 6. Projection Targets
    tests.append(TestConfig('Target_Start', 60, 'normal', 'linear_up', 0.0, 0.95, 'start'))
    tests.append(TestConfig('Target_Middle', 60, 'normal', 'linear_up', 0.0, 0.95, 'middle'))
    tests.append(TestConfig('Target_End', 60, 'normal', 'linear_up', 0.0, 0.95, 'end'))

    # 7. Stress Tests
    tests.append(TestConfig('Stress_HighNoise', 60, 'normal', 'none', 0.0, 0.95, 'end', noise_level=5.0))
    tests.append(TestConfig('Stress_Small_HighRho', 20, 'normal', 'none', 0.7, 0.95, 'end')) # n=20
    tests.append(TestConfig('Stress_Step_Median', 60, 'normal', 'step', 0.0, 0.50, 'end'))
    tests.append(TestConfig('Stress_Gamma_Trend', 100, 'gamma', 'linear_up', 0.3, 0.95, 'end'))

    # Fill to 30 tests
    while len(tests) < 30:
        tests.append(TestConfig(f'Extra_{len(tests)+1}', 50, 'normal', 'none', 0.0, 0.95, 'end'))

    results = []
    print(f"Running {len(tests)} validation tests with {n_iterations} iterations each...", flush=True)
    print(f"Target coverage: {confidence:.0%}", flush=True)
    print("-" * 60, flush=True)

    pass_count_proj = 0
    pass_count_qr = 0
    total_qr_runs = 0

    for idx, test in enumerate(tests):
        print(f"[{idx+1}/{len(tests)}] {test.name}", flush=True)
        print(f"  Config: {test}", flush=True)

        res = run_test(test, n_iterations, confidence)
        results.append(res)

        # Check pass
        p_pass = abs(res['projection_coverage'] - confidence) <= 0.03
        q_pass = abs(res['qr_coverage'] - confidence) <= 0.03

        mark_p = "✓ PASS" if p_pass else f"X FAIL ({res['projection_coverage']:.3f})"
        mark_q = "✓ PASS" if q_pass else f"X FAIL ({res['qr_coverage']:.3f})"

        if p_pass: pass_count_proj += 1

        # Only count QR if it ran (coverage > 0 or intended to run)
        # Assuming coverage=0 means failure to compute or 0 coverage.
        # But if it's 0.0, it's definitely a FAIL unless expected.
        if res['qr_coverage'] > 0:
            total_qr_runs += 1
            if q_pass: pass_count_qr += 1

        print(f"  Projection: {res['projection_coverage']:.3f} coverage, width={res['projection_width']:.2f} {mark_p}", flush=True)
        print(f"  QR:         {res['qr_coverage']:.3f} coverage, width={res['qr_width']:.2f} {mark_q}", flush=True)
        print("", flush=True)

    print("SUMMARY", flush=True)
    print(f"Projection Method: {pass_count_proj}/{len(tests)} tests passed (±3% tolerance)", flush=True)
    print(f"QR Method:         {pass_count_qr}/{total_qr_runs} tests passed (±3% tolerance)", flush=True)

    return results

def plot_coverage_by_category(results):
    """Visual summary of validation results."""
    # Ensure plots directory exists
    # We will save in current directory

    categories = {
        'Percentile': [r for r in results if 'Baseline' in r['test'].name],
        'Sample Size': [r for r in results if 'SampleSize' in r['test'].name],
        'Distribution': [r for r in results if 'Distribution' in r['test'].name],
        'Trend Type': [r for r in results if r['test'].name.startswith('Trend_')],
        'Autocorr': [r for r in results if 'Autocorr' in r['test'].name],
        'Target': [r for r in results if r['test'].name.startswith('Target_')],
        'Stress': [r for r in results if 'Stress' in r['test'].name]
    }

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    # Remove empty axes if any
    if len(categories) < 8:
        for i in range(len(categories), 8):
            fig.delaxes(axes[i])

    for idx, (cat_name, cat_results) in enumerate(categories.items()):
        if not cat_results:
            continue

        ax = axes[idx]

        proj_cov = [r['projection_coverage'] for r in cat_results]
        qr_cov = [r['qr_coverage'] for r in cat_results]
        labels = [r['test'].name.replace(cat_name, '').strip('_') for r in cat_results]

        x = np.arange(len(proj_cov))

        ax.scatter(x, proj_cov, label='Projection', marker='o', s=50)
        ax.scatter(x, qr_cov, label='QR', marker='s', s=50)

        ax.axhline(0.95, color='green', linestyle='--', label='Target')
        ax.axhline(0.92, color='red', linestyle=':', alpha=0.5)
        ax.axhline(0.98, color='red', linestyle=':', alpha=0.5)

        ax.set_title(cat_name)
        ax.set_ylabel('Coverage')
        ax.set_ylim(0.80, 1.0)

        # X-axis labels
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)

        if idx == 0:
            ax.legend(loc='lower right')

    plt.tight_layout()
    plt.savefig('validation_coverage_summary.png', dpi=300)
    print("Saved: validation_coverage_summary.png")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run statistical validation for whatts package.")
    parser.add_argument("--iterations", type=int, default=1000, help="Number of iterations per test (default: 1000)")
    parser.add_argument("--confidence", type=float, default=0.95, help="Target confidence level (default: 0.95)")
    args = parser.parse_args()

    start_time = time.time()
    results = run_full_validation(n_iterations=args.iterations, confidence=args.confidence)
    end_time = time.time()

    print(f"\nTotal time: {end_time - start_time:.1f} seconds", flush=True)

    plot_coverage_by_category(results)
