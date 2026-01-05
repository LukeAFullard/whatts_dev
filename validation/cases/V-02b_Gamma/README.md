# Validation Case: V-02b_Gamma

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
*   **Target Percentile:** 0.95
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
| **Projection (N=30)** | 200 | 0.95 | 0.875 | 8.837 | FAIL |
| **Projection (N=60)** | 200 | 0.95 | 0.965 | 6.571 | PASS |
| **Projection (N=100)** | 200 | 0.95 | 0.945 | 4.540 | PASS |
| **Projection (N=200)** | 200 | 0.95 | 0.930 | 2.948 | PASS |
| **Quantile Regression** | - | - | - | - | SKIPPED |

## 7. Interpretation & Conclusion
**Analysis:**
The Projection (Wilson-Hazen) method performs well for sample sizes N >= 60, achieving coverage probabilities within the target range. However, at N=30, the method fails (87.5% coverage vs 95% target), likely due to the inherent skewness of the Gamma distribution which the normal-approximation based Wilson interval struggles with at small sample sizes.

**Anomalies:**
Quantile Regression tests were skipped to save time and will be run separately.
