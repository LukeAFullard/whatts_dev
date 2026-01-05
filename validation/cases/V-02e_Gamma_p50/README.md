# Validation Case: V-02e_Gamma_p50

## 1. Objective
**What is being tested:**
Verify that methods handle non-normal Gamma data without excessive coverage error.

**Category:**
Distribution Robustness

## 2. Rationale
**Why this test is important:**
Gamma distributions are often used for precipitation or flows. We must ensure the method remains robust.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 30, 60, 100, 200
*   **Distribution:** Gamma (shape=2.0, scale=2.0)
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentile:** 0.50
*   **Iterations:** 200

## 4. Methodology
**Execution Strategy:**
This test runs a Monte Carlo simulation using the scripts in this folder.
1.  Generate synthetic data based on the parameters above.
2.  Apply `whatts` methods.
3.  Calculate **Actual Coverage**.
4.  Compare against **Target Coverage**.

## 5. Success Criteria
**Pass/Fail Definition:**
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
