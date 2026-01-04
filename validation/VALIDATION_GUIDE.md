# Validation Guide for whatts Package

## Overview

This guide validates that both methods (Projection and Quantile Regression) achieve correct **coverage probability**. For 95% confidence intervals, the Upper Tolerance Limit (UTL) should exceed the true percentile in 95% of repeated experiments.

**Target**: Coverage within ±3% of nominal level (92-98% for 95% CI)

---

## Prerequisites

```bash
pip install whatts numpy pandas scipy matplotlib
```

Required files:
- `validation_plan.py` (included in the `validation/` directory)
- `whatts` package installed

---

## Step 1: Quick Validation Run

Run baseline validation (5 minutes):

```bash
python validation/validation_plan.py
```

This executes 30 tests × 1000 iterations = 30,000 simulations.

**Expected output:**
```
Running 30 validation tests with 1000 iterations each...
Target coverage: 95%

[1/30] Baseline_p50
  Config: Test(n=50, dist=normal, trend=none, p=0.5, ρ=0.0, target=end)
  Projection: 0.951 coverage, width=1.23 ✓ PASS
  QR:         0.948 coverage, width=1.31 ✓ PASS
...

SUMMARY
Projection Method: 28/30 tests passed (±3% tolerance)
QR Method:         24/27 tests passed (±3% tolerance)
```

---

## Step 2: Interpret Results

### Coverage Metrics

**Pass criteria:**
- `0.92 ≤ coverage ≤ 0.98` for 95% confidence
- Failures indicate either:
  - Under-coverage (<0.92): Intervals too narrow, false confidence
  - Over-coverage (>0.98): Intervals too wide, loss of statistical power

### Interval Width

- **Narrower is not better** if coverage is inadequate
- Compare methods: QR should have similar/slightly wider intervals for heteroscedastic data
- Width increases with: autocorrelation, higher percentiles, smaller n

### Common Failure Patterns

| Failure Type | Likely Cause | Action |
|-------------|--------------|--------|
| Under-coverage (both methods) | True percentile calculation error | Check `generate_series()` math |
| Under-coverage (Projection only) | n_eff adjustment inadequate | Check AR(1) formula for high ρ |
| Under-coverage (QR only) | Bootstrap block size wrong | Adjust for seasonality |
| QR failures > Projection | Insufficient n for tail estimation | Expected for n<50 |

---

## Step 3: Deep Validation (Publication Quality)

For paper submission, run extended validation (2-4 hours):

```python
# Edit validation_plan.py:
results = run_full_validation(n_iterations=10000, confidence=0.95)
```

**Monte Carlo error**: With 10,000 iterations, standard error ≈ 0.2%, so ±3% tolerance is conservative.

---

## Step 4: Test-by-Test Analysis

### Category 1: Percentile Coverage

**Tests 1-6**: Verify all percentiles (50th, 75th, 95th) work correctly.

**Expected behavior:**
- 50th percentile: Both methods converge quickly
- 75th percentile: Projection slightly better at small n
- 95th percentile: QR superior for heteroscedastic data

**Red flags:**
- 50th percentile fails → fundamental error in Hazen interpolation
- Only 95th fails → tail estimation issue

---

### Category 2: Sample Size Effects

**Tests 7-9**: n=30, 60, 120

**Expected behavior:**
- n=30: Projection coverage ~0.93-0.97 (wider tolerance), QR may under-cover
- n=60: Both methods achieve 0.94-0.96
- n=120: Both converge to 0.945-0.955

**Red flags:**
- Coverage improves then degrades → boundary correction bug
- QR fails at n=120 → bootstrap implementation error

---

### Category 3: Distribution Types

**Tests 10-13**: Normal, lognormal, gamma, uniform

**Expected behavior:**
- Normal: Best performance (matches theory)
- Lognormal: Projection may slightly under-cover (right-skew challenge)
- Gamma: QR more robust
- Uniform: Both excellent (bounded support)

**Red flags:**
- Failures on normal only → core algorithm issue
- Failures on skewed only → Hazen plotting position bias

---

### Category 4: Trend Types

**Tests 14-18**: None, linear up/down, quadratic, step

**Expected behavior:**
- Linear trends: Both methods excel
- Quadratic: Projection under-covers (assumes linearity)
- Step change: Both may struggle (regime shift)

**Red flags:**
- Linear trend fails → Mann-Kendall or projection math wrong
- All trends fail similarly → not properly removing trend

---

### Category 5: Autocorrelation

**Tests 19-22**: ρ=0.0, 0.3, 0.6, 0.9

**Expected behavior:**
- ρ=0.0: Baseline performance
- ρ=0.3: Slight widening, coverage maintained
- ρ=0.6: Noticeable widening, n_eff ≈ n/2
- ρ=0.9: Large widening, n_eff ≈ n/5-10

**Red flags:**
- Under-coverage at ρ=0.6+: n_eff formula inadequate
- Over-coverage throughout: Too conservative correction

---

### Category 6: Projection Targets

**Tests 23-25**: Start, middle, end

**Expected behavior:**
- All achieve similar coverage
- Width differs based on extrapolation distance
- Start = most conservative (longest extrapolation for improving sites)

**Red flags:**
- 'Middle' fails but others pass → time calculation bug
- Coverage diverges >5% between targets → projection math error

---

### Category 7: Stress Tests

**Tests 26-28**: Edge cases

**Test 26 (High Noise):**
- Expect wider intervals, coverage ~0.94-0.96
- Failure → signal/noise ratio detection issue

**Test 27 (Small n + High ρ):**
- Expect n_eff < 10, very wide intervals
- Projection may slightly under-cover (n_eff formula limit)
- QR should refuse (convergence failure)

**Test 28 (Median + Step Change):**
- Both methods may under-cover slightly (0.92-0.93)
- Acceptable if documented limitation

---

## Step 5: Generate Diagnostic Plots

Add after test completion:

```python
import matplotlib.pyplot as plt

def plot_coverage_by_category(results):
    """Visual summary of validation results."""

    categories = {
        'Percentile': [r for r in results if 'Baseline' in r['test'].name or 'Trend_p' in r['test'].name],
        'Sample Size': [r for r in results if 'SampleSize' in r['test'].name],
        'Distribution': [r for r in results if 'Distribution' in r['test'].name],
        'Trend Type': [r for r in results if r['test'].name.startswith('Trend_')],
        'Autocorr': [r for r in results if 'Autocorr' in r['test'].name],
        'Target': [r for r in results if r['test'].name.startswith('Target_')],
        'Stress': [r for r in results if 'Stress' in r['test'].name]
    }

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()

    for idx, (cat_name, cat_results) in enumerate(categories.items()):
        ax = axes[idx]

        proj_cov = [r['projection_coverage'] for r in cat_results]
        qr_cov = [r['qr_coverage'] for r in cat_results if not np.isnan(r['qr_coverage'])]

        x = range(len(proj_cov))
        ax.scatter(x, proj_cov, label='Projection', alpha=0.7)
        ax.scatter(range(len(qr_cov)), qr_cov, label='QR', alpha=0.7)

        ax.axhline(0.95, color='green', linestyle='--', label='Target')
        ax.axhline(0.92, color='red', linestyle=':', alpha=0.5)
        ax.axhline(0.98, color='red', linestyle=':', alpha=0.5)

        ax.set_title(cat_name)
        ax.set_ylabel('Coverage')
        ax.set_ylim(0.85, 1.0)
        ax.legend()

    plt.tight_layout()
    plt.savefig('validation_coverage_summary.png', dpi=300)
    print("Saved: validation_coverage_summary.png")

# Run after validation
plot_coverage_by_category(results)
```

---

## Step 6: Document Findings

Create `VALIDATION_REPORT.md`:

```markdown
# Validation Report

**Date**: YYYY-MM-DD
**Iterations**: 10,000 per test
**Target Coverage**: 95% (±3% tolerance)

## Overall Results
- Projection Method: X/30 tests passed
- QR Method: X/27 tests passed

## Known Limitations
1. [If quadratic trends fail]: Methods assume linear trends
2. [If high ρ fails]: AR(1) approximation breaks down at ρ>0.8
3. [If QR fails at n=30]: QR requires n≥50 for stable 95th percentile

## Recommendations
- Use Projection for: [conditions where it excels]
- Use QR for: [conditions where it excels]
- Avoid both for: [documented failure modes]
```

---

## Step 7: Regression Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/validation.yml
name: Statistical Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run quick validation
        run: |
          python validation/validation_plan.py > validation_output.txt
          # Check for failures
          grep "SUMMARY" validation_output.txt
```

**Pass criteria for CI**: ≥90% of tests pass (27/30)
