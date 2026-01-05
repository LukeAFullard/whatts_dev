# Validation Case: V-01d_p99

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the Extreme Percentile (p99) for a standard normal distribution with no trend and no autocorrelation.

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
*   **Target Percentile:** 0.99
*   **Iterations:** 200
*   **Confidence Level:** 0.95 (Two-Sided)

## 4. Methodology
**Execution Strategy:**
This folder contains multiple scripts to test different sample sizes and methods independently to avoid timeouts.
1.  Generate standard normal data.
2.  Apply `whatts` methods (Projection and Quantile Regression).
3.  Calculate **Actual Interval Coverage**: The proportion of simulations where the **Two-Sided Interval** ($LTL \le True \le UTL$) contains the true underlying percentile (2.3263).
4.  Compare against **Target Coverage** (0.95).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (0.95).

*   **PASS:** $|Actual - 0.95| \le 0.03$
*   **FAIL:** $|Actual - 0.95| > 0.03$

## 6. Results Summary
*Note: These results are automatically appended to `validation/master_results.csv`.*

| Method | N | Target Coverage | Actual Coverage | Avg Width | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Projection** | 30 | 0.95 | 0.8650 | 4.1344 | FAIL |
| **Projection** | 60 | 0.95 | 0.8350 | 2.4262 | FAIL |
| **Projection** | 100 | 0.95 | 0.8650 | 1.8627 | FAIL |
| **Projection** | 200 | 0.95 | 0.8600 | 0.9899 | FAIL |
| **Quantile Regression** | 30 | 0.95 | 0.7350 | 2.8824 | FAIL |
| **Quantile Regression** | 60 | 0.95 | 0.6550 | 2.0972 | FAIL |
| **Quantile Regression** | 100 | 0.95 | 0.6750 | 1.8016 | FAIL |
| **Quantile Regression** | 200 | 0.95 | N/A | N/A | Terminated (Run Locally) |

## 7. Interpretation & Conclusion
**Analysis:**
Both the **Projection (Wilson-Hazen)** and **Quantile Regression (QR)** methods consistently fail to achieve the target coverage of 95% for the 99th percentile.

*   **Projection:** Exhibits systematic under-coverage (approx. 83-86%). The Probit interpolation, while useful for extrapolation, appears to underestimate the uncertainty at the extreme 99th percentile.
*   **Quantile Regression:** Performs significantly worse (65-73%), likely due to the inherent difficulty of non-parametric bootstrapping for extreme tails with limited sample sizes. N=200 was terminated due to runtime constraints but is expected to follow the same trend.

**Recommendation:**
Users should exercise extreme caution when interpreting p99 estimates, especially with sample sizes $N < 200$. The "High Confidence Failure" or "Compliance" determinations based on p99 may be overly optimistic (i.e., narrower intervals than reality).
