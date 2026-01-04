# whatts Validation Plan

This document outlines a comprehensive plan for verifying the `whatts` Python package. The goal is to ensure that both the **Projection** (Wilson-Hazen) and **Quantile Regression** (QR) methods achieve correct coverage probabilities and produce reliable tolerance limits under a wide variety of conditions.

## Verification Methodology

To ensure isolation and reproducibility, the validation suite is organized into discrete, self-contained test cases.

### Folder Structure
Each verification test is housed in its own numbered directory under `validation/cases/`.
*   Example: `validation/cases/V-01_Baseline_Percentiles/`
*   Example: `validation/cases/V-02_Sample_Size/`

### Self-Contained Execution
There is **no master runner**. Each test folder contains a self-contained Python script (e.g., `run_test.py`) that:
1.  Generates the specific synthetic data for that case.
2.  Runs the `whatts` analysis (both Projection and QR methods).
3.  Calculates coverage statistics over $N$ iterations (default: 1000).
4.  Appends the results to the Master Results Tracking file.

To run a specific test:
```bash
python validation/cases/V-01_Baseline_Percentiles/run_test.py
```

### Master Results Tracking
A master CSV file, `validation/master_results.csv`, will be created and updated by each test script. This file serves as the single source of truth for validation status.

**Columns:**
*   `test_id`: Unique identifier (e.g., "V-01_p50").
*   `scenario`: Description of the specific condition (e.g., "Target Percentile 50%").
*   `method`: "Projection" or "QuantileRegression".
*   `iterations`: Number of Monte Carlo simulations run.
*   `target_coverage`: The nominal confidence level (e.g., 0.95).
*   `actual_coverage`: The fraction of simulations where the UTL exceeded the true percentile.
*   `avg_width`: The average width of the tolerance interval (UTL - Point Estimate).
*   `pass_status`: "PASS" if `actual_coverage` is within ±3% of `target_coverage`, else "FAIL".
*   `timestamp`: Time of execution.

---

## Verification Scenarios

### Category 1: Baseline Performance

#### V-01: Baseline Percentile Accuracy
**Objective**: Verify that both methods correctly estimate various percentiles for a standard normal distribution with no trend and no autocorrelation.
**Data Description**: $N=50$, Normal distribution, no trend, $\rho=0$.
**Scenarios**:
*   **Median (p50)**: Test central tendency coverage.
*   **Upper Quartile (p75)**: Test moderate tail coverage.
*   **High Percentile (p95)**: Test standard compliance tail coverage.
*   **Extreme Percentile (p99)**: Test extreme tail extrapolation.

### Category 2: Sample Size Sensitivity

#### V-02: Sample Size Effects
**Objective**: Determine the minimum sample size required for stable estimates and verify that coverage converges as $N$ increases.
**Data Description**: Normal distribution, no trend, $\rho=0$, Target $p=0.95$.
**Scenarios**:
*   **Small (N=30)**: Validates performance at the lower bound of recommended data size.
*   **Medium (N=60)**: Represents a typical monitoring dataset (5 years of monthly data).
*   **Large (N=120)**: Represents a robust dataset (10 years of monthly data).
*   **Very Large (N=200)**: Asymptotic check.

### Category 3: Distribution Robustness

#### V-03: Non-Normal Distributions
**Objective**: Verify that methods (especially Quantile Regression) handle non-normal data without excessive coverage error.
**Data Description**: $N=100$, no trend, $\rho=0$, Target $p=0.95$.
**Scenarios**:
*   **Lognormal**: Right-skewed data common in environmental concentrations.
*   **Gamma**: Skewed data often used for precipitation or flows.
*   **Uniform**: Bounded distribution to test edge behavior.

### Category 4: Trend Handling

#### V-04: Linear Trends
**Objective**: Ensure that trend detection and removal (Projection) or modeling (QR) works for monotonic changes.
**Data Description**: $N=60$, Normal distribution, $\rho=0$, Target $p=0.95$.
**Scenarios**:
*   **Linear Up**: Moderate increasing trend ($0.05\sigma/t$).
*   **Linear Down**: Moderate decreasing trend ($-0.05\sigma/t$).

#### V-05: Nonlinear Trends
**Objective**: Test robustness against model misspecification (Projection assumes linearity).
**Data Description**: $N=60$, Normal distribution, $\rho=0$, Target $p=0.95$.
**Scenarios**:
*   **Quadratic**: A curved trend ($y \propto t^2$).
*   **Step Change**: A sudden shift in mean (Regime change).

### Category 5: Autocorrelation Handling

#### V-06: Autocorrelation Correction
**Objective**: Verify the Effective Sample Size ($n_{eff}$) adjustments and block bootstrapping. High autocorrelation reduces information content, requiring wider intervals to maintain coverage.
**Data Description**: $N=100$, Normal distribution, no trend, Target $p=0.95$.
**Scenarios**:
*   **Low ($\rho=0.3$)**: Minor serial correlation.
*   **Moderate ($\rho=0.6$)**: Significant serial correlation.
*   **High ($\rho=0.8$)**: Strong persistence.
*   **High + Trend**: Linear trend with $\rho=0.6$ noise.

### Category 6: Projection Targets

#### V-07: Target Date Sensitivity
**Objective**: Verify that the system correctly projects tolerance limits to different points in time.
**Data Description**: $N=60$, Linear Up trend, Target $p=0.95$.
**Scenarios**:
*   **Start**: Retrospective analysis (Project to $t=0$).
*   **Middle**: Mid-period analysis (Project to $t=N/2$).
*   **End**: Current state analysis (Project to $t=N$).

### Category 7: Stress Tests & Edge Cases

#### V-08: Stress Tests
**Objective**: Push the methods to their breaking points to identify failure modes.
**Scenarios**:
*   **High Noise**: Signal-to-noise ratio is very low. Tests trend detection robustness.
*   **Small N + High Rho**: $N=20, \rho=0.7$. Extremely low effective sample size ($n_{eff} < 10$). Should trigger warnings and potentially wide intervals.
*   **Step + Median**: Step trend looking at the 50th percentile.
*   **Mixed Distribution + Trend**: Gamma distribution with a linear trend and moderate autocorrelation.
