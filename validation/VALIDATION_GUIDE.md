# whatts Validation Plan

This document outlines a comprehensive plan for verifying the `whatts` Python package. The goal is to ensure that both the **Projection** (Wilson-Hazen) and **Quantile Regression** (QR) methods achieve correct coverage probabilities and produce reliable tolerance limits under a wide variety of conditions.

## Verification Methodology

To ensure isolation and reproducibility, the validation suite is organized into discrete, self-contained test cases.

### Folder Structure
Each verification test is housed in its own numbered directory under `validation/cases/`.
*   Example: `validation/cases/V-01_Baseline_Percentiles/`
*   Example: `validation/cases/V-02_NonNormal_Distributions/`

### Documentation Standard (README.md)
Every test folder **must** contain a `README.md` file derived from `validation/VALIDATION_TEMPLATE.md`. This ensures consistent documentation of:
*   Test Rationale & Objective
*   Success Criteria
*   Data Generation Parameters
*   Interpretation of Results

### Self-Contained Execution
There is **no master runner**. Each test folder contains a self-contained Python script (e.g., `run_test.py`) that:
1.  Generates the specific synthetic data for that case.
2.  Runs the `whatts` analysis (both Projection and QR methods).
    *   **Configuration:** All tests must run with `sides=2` (Two-Sided Confidence Intervals) as the default.
3.  Calculates coverage statistics over $N$ iterations (default: 1000).
    *   **Success Metric:** For a Two-Sided 95% Confidence Interval, the Target Coverage is **0.95**. Validation checks should verify if the true value falls between the Lower and Upper Tolerance Limits.
4.  Appends the results to the Master Results Tracking file.

To run a specific test:
```bash
python validation/cases/V-01_Baseline_Percentiles/run_test.py
```

### Managing Long-Running Tests
The **Quantile Regression (QR)** method is computationally intensive due to bootstrapping. If a test case involves many iterations or large sample sizes, it should be **split** into multiple sub-cases to keep runtime manageable (< 10-15 minutes per script).

**Naming Convention for Split Tests:**
Use alphabetic suffixes (e.g., `V-02a`, `V-02b`) or file names indicating the scenario (e.g., `run_test_N30.py`).

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
**Data Description**: Normal distribution, no trend, $\rho=0$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Scenarios**:
*   **Median (p50)**: Test central tendency coverage.
*   **Upper Quartile (p75)**: Test moderate tail coverage.
*   **High Percentile (p95)**: Test standard compliance tail coverage.
*   **Extreme Percentile (p99)**: Test extreme tail extrapolation.

### Category 2: Distribution Robustness

#### V-02: Non-Normal Distributions
**Objective**: Verify that methods (especially Quantile Regression) handle non-normal data without excessive coverage error.
**Data Description**: No trend, $\rho=0$, Target $p=0.95$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Scenarios**:
*   **Lognormal**: Right-skewed data common in environmental concentrations.
*   **Gamma**: Skewed data often used for precipitation or flows.
*   **Uniform**: Bounded distribution to test edge behavior.

### Category 3: Trend Handling

#### V-03: Linear Trends
**Objective**: Ensure that trend detection and removal (Projection) or modeling (QR) works for monotonic changes.
**Data Description**: Normal distribution, $\rho=0$, Target $p=0.95$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Scenarios**:
*   **Linear Up**: Moderate increasing trend ($0.05\sigma/t$).
*   **Linear Down**: Moderate decreasing trend ($-0.05\sigma/t$).

#### V-04: Nonlinear Trends
**Objective**: Test robustness against model misspecification (Projection assumes linearity).
**Data Description**: Normal distribution, $\rho=0$, Target $p=0.95$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Scenarios**:
*   **Quadratic**: A curved trend ($y \propto t^2$).
*   **Step Change**: A sudden shift in mean (Regime change).

### Category 4: Autocorrelation Handling (Split Recommended)

#### V-05: Autocorrelation Correction
**Objective**: Verify the Effective Sample Size ($n_{eff}$) adjustments and block bootstrapping. High autocorrelation reduces information content, requiring wider intervals to maintain coverage.
**Data Description**: Normal distribution, no trend, Target $p=0.95$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Note**: Split into sub-folders as high autocorrelation often requires more iterations or careful checking.
*   **V-05a**: Low Autocorrelation ($\rho=0.3$).
*   **V-05b**: Moderate Autocorrelation ($\rho=0.6$).
*   **V-05c**: High Autocorrelation ($\rho=0.8$).
*   **V-05d**: High + Trend. Linear trend with $\rho=0.6$ noise.

### Category 5: Projection Targets

#### V-06: Target Date Sensitivity
**Objective**: Verify that the system correctly projects tolerance limits to different points in time.
**Data Description**: Linear Up trend, Target $p=0.95$. Test with **$N \in \{30, 60, 100, 200\}$**.
**Scenarios**:
*   **Start**: Retrospective analysis (Project to $t=0$).
*   **Middle**: Mid-period analysis (Project to $t=N/2$).
*   **End**: Current state analysis (Project to $t=N$).

### Category 6: Stress Tests & Edge Cases (Split Recommended)

#### V-07: Stress Tests
**Objective**: Push the methods to their breaking points to identify failure modes.
**Data Description**: Various. Test with **$N \in \{30, 60, 100, 200\}$** where applicable.
**Scenarios**:
*   **V-07a_High_Noise**: Signal-to-noise ratio is very low.
*   **V-07b_Small_N_High_Rho**: $N=20, \rho=0.7$. Extremely low effective sample size ($n_{eff} < 10$). (Note: fixed N here due to nature of test).
*   **V-07c_Step_Median**: Step trend looking at the 50th percentile.
*   **V-07d_Mixed**: Gamma distribution with a linear trend and moderate autocorrelation.
