# Validation Case: V-01b_p75

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the Upper Quartile (p75) for a standard normal distribution with no trend and no autocorrelation.

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
*   **Autocorrelation ($ho$):** 0.0
*   **Target Percentile:** 0.75
*   **Iterations:** 1000

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
Results are appended to `validation/master_results.csv`.
