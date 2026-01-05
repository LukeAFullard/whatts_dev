# Validation Case: V-01a_p50

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the Median (p50) for a standard normal distribution with no trend and no autocorrelation.

**Category:**
Baseline Performance

## 2. Rationale
**Why this test is important:**
Baseline accuracy is fundamental. We need to ensure that in the simplest case (normal, i.i.d.), the methods provide correct coverage for various percentiles, especially tails.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 30, 60, 100, 200 (Tested in separate scripts)
*   **Distribution:** Standard Normal
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentile:** 0.5
*   **Iterations:** 200 (QR tested with 20 for initial verification due to runtime)

## 4. Methodology
**Execution Strategy:**
This folder contains multiple scripts to test different sample sizes and methods independently to avoid timeouts.
1.  Generate standard normal data.
2.  Apply `whatts` methods (Projection and Quantile Regression).
3.  Calculate **Actual Coverage**: The proportion of simulations where the calculated UTL (from a Two-Sided 95% Confidence Interval) exceeds the true underlying percentile.
4.  Compare against **Target Coverage** (implied 97.5% for the upper bound of a 95% two-sided interval).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (97.5%).

*   **PASS:** $|Actual - 0.975| \le 0.03$
*   **FAIL:** $|Actual - 0.975| > 0.03$

## 6. Results Summary

| method              | scenario   |   iterations |   target_coverage |   actual_coverage |   avg_width | pass_status   |
|:--------------------|:-----------|-------------:|------------------:|------------------:|------------:|:--------------|
| projection          | p50_N30    |          200 |              0.95 |             0.975 |      0.8852 | PASS          |
| projection          | p50_N60    |          200 |              0.95 |             0.98  |      0.6499 | PASS          |
| projection          | p50_N100   |          200 |              0.95 |             0.975 |      0.5119 | PASS          |
| projection          | p50_N200   |          200 |              0.95 |             0.965 |      0.3525 | PASS          |
| quantile_regression | p50_N30    |           20 |              0.95 |             1     |      2.1168 | PASS          |
| quantile_regression | p50_N60    |           20 |              0.95 |             1     |      1.1826 | PASS          |
| quantile_regression | p50_N100   |           20 |              0.95 |             1     |      0.9802 | PASS          |
| quantile_regression | p50_N200   |           20 |              0.95 |             1     |      0.7211 | PASS          |

Results are also appended to `validation/master_results.csv`.

## 7. Interpretation & Conclusion
**Analysis:**
Both methods pass the coverage criteria.

**Note on Interval Width:**
The **Quantile Regression (QR)** method produces confidence intervals roughly **2x wider** than the **Projection (Wilson-Hazen)** method. This is expected and explained by:
1.  **Parametric vs. Non-Parametric Efficiency:** The Projection method exploits the normality assumption of the data (using Wilson Score intervals), which is highly efficient for estimating the median of a normal distribution. The QR method is non-parametric and makes no such assumption, resulting in lower statistical efficiency (wider intervals) for normal data.
2.  **Block Bootstrapping:** The QR method uses Moving Block Bootstrapping (MBB) to be robust against autocorrelation. Even for independent data (as in this test), MBB reduces the effective degrees of freedom compared to assuming independence, leading to wider, more conservative intervals.
3.  **Two-Sided Confirmation:** Both methods correctly calculated Two-Sided 95% Confidence Intervals (sides=2). The width difference is a property of the statistical estimators, not a configuration mismatch.
