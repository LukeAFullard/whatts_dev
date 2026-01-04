# Validation Case: [V-XX_Name]

## 1. Objective
**What is being tested:**
[Brief description of the specific scenario, e.g., "Verify coverage for small sample sizes (N=30)."]

**Category:**
[E.g., Baseline Performance, Sample Size Sensitivity, Trend Handling, etc.]

## 2. Rationale
**Why this test is important:**
[Explanation of why this validation is necessary. E.g., "Small sample sizes are common in monitoring data; we must ensure the method remains conservative."]

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** [e.g., 30]
*   **Distribution:** [e.g., Normal, Lognormal, Gamma]
*   **Trend:** [e.g., None, Linear Up (slope=0.05), Step Change]
*   **Autocorrelation ($\rho$):** [e.g., 0.0, 0.6]
*   **Target Percentile:** [e.g., 0.95]
*   **Iterations:** [e.g., 1000]

## 4. Methodology
**Execution Strategy:**
This test runs a Monte Carlo simulation using the script in this folder (`run_test.py`).
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
[Discuss how the methods performed. Did one outperform the other? Were the results expected given the data characteristics?]

**Anomalies:**
[Did any runs fail or produce warnings? Discuss any specific edge cases encountered.]
