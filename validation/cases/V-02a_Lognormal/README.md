# Validation Case: V-02a_Lognormal

## 1. Objective
**What is being tested:**
Verify that methods (especially Quantile Regression) handle non-normal Lognormal data without excessive coverage error.

**Category:**
Distribution Robustness

## 2. Rationale
**Why this test is important:**
Lognormal distributions are common in environmental concentrations. We must ensure the method remains robust when the normality assumption is violated.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 30, 60, 100, 200
*   **Distribution:** Lognormal (mean=0, sigma=1)
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentile:** 0.95
*   **Iterations:** 200 (Default for validation to ensure timely execution)

## 4. Methodology
**Execution Strategy:**
This test runs a Monte Carlo simulation using the scripts in this folder (e.g., `run_test_N30_WH.py`).
1.  Generate synthetic data based on the parameters above.
2.  Apply `whatts` methods:
    *   **Projection:** Wilson-Hazen with Detrending.
    *   **Quantile Regression:** Moving Block Bootstrap.
3.  Calculate **Actual Coverage**: The proportion of simulations where the calculated UTL exceeds the true underlying percentile.
4.  Compare against **Target Coverage** (confidence level).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (e.g., for 95% confidence, coverage must be between 92% and 98%).

*   **PASS:** $|Actual - Target| \le 0.03$
*   **FAIL:** $|Actual - Target| > 0.03$

## 6. Results Summary
*Note: These results are automatically appended to `validation/master_results.csv`.*

| Method | Iterations | Target Coverage | Actual Coverage | Avg Width | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Projection** | [N] | [0.XX] | [0.XX] | [X.XX] | [PASS/FAIL] |
| **Quantile Regression** | [N] | [0.XX] | [0.XX] | [X.XX] | [PASS/FAIL] |

## 7. Interpretation & Conclusion
**Analysis:**
[To be filled after execution]

**Anomalies:**
[To be filled after execution]
