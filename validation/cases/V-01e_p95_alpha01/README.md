# Validation Case: V-01e_p95_alpha01

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the High Percentile (p95) for a standard normal distribution with no trend and no autocorrelation, specifically targeting a **90% Confidence Level (alpha = 0.1)**.

**Category:**
Baseline Performance

## 2. Rationale
**Why this test is important:**
We need to ensure that the library correctly handles different confidence levels, not just the standard 0.95. This test validates that changing the alpha parameter correctly adjusts the interval widths and coverage probabilities.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 30, 60, 100, 200 (Tested in separate scripts)
*   **Distribution:** Standard Normal
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentile:** 0.95
*   **Iterations:** 200 (Reduced from 1000 for performance)
*   **Target Confidence:** 0.90 (alpha = 0.10)

## 4. Methodology
**Execution Strategy:**
This folder contains multiple scripts to test different sample sizes and methods independently to avoid timeouts.
1.  Generate standard normal data.
2.  Apply `whatts` methods (Projection and Quantile Regression) with `confidence=0.9`.
3.  Calculate **Actual Coverage**: The proportion of simulations where the true underlying percentile falls within the calculated Two-Sided 90% Confidence Interval (LTL $\le$ True $\le$ UTL).
4.  Compare against **Target Coverage** (0.90).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (0.90).

*   **PASS:** $|Actual - 0.90| \le 0.03$ (i.e., 0.87 to 0.93)
*   **FAIL:** $|Actual - 0.90| > 0.03$

## 6. Results Summary
Results are appended to `validation/master_results.csv`.

| Method | N | Target | Actual Coverage | Avg Width | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Projection** | 30 | 0.90 | 0.8500 | 1.54 | FAIL |
| **Projection** | 60 | 0.90 | 0.8750 | 1.07 | PASS |
| **Projection** | 100 | 0.90 | 0.8700 | 0.76 | FAIL |
| **Projection** | 200 | 0.90 | 0.8800 | 0.52 | PASS |
| **Quantile Regression** | 30 | 0.90 | Running... | TBD | TBD |
| **Quantile Regression** | 60 | 0.90 | Running... | TBD | TBD |
| **Quantile Regression** | 100 | 0.90 | Running... | TBD | TBD |
| **Quantile Regression** | 200 | 0.90 | Running... | TBD | TBD |

## 7. Interpretation & Conclusion
**Analysis:**
Initial results for the Projection method show mixed performance:
*   **Projection (Wilson-Hazen):**
    *   **N=30:** Fails with significant under-coverage (0.85 vs 0.90).
    *   **N=60:** Passes (0.875).
    *   **N=100:** Fails marginally (0.870 vs 0.90 target, diff 0.03).
    *   **N=200:** Passes (0.880).

    The method seems to struggle slightly with this specific confidence/percentile combination, tending towards the lower bound of the acceptance criteria.

*   **Quantile Regression:** Tests are currently running.
