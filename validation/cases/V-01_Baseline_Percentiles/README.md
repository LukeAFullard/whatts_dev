# Validation Case: V-01: Baseline Percentile Accuracy

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate various percentiles for a standard normal distribution with no trend and no autocorrelation.

**Category:**
Baseline Performance

## 2. Rationale
**Why this test is important:**
Baseline validation ensures that the core statistical engines (Wilson-Hazen and Quantile Regression) are calibrated correctly under ideal conditions. If a method fails here, it will fail in more complex scenarios.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 50
*   **Distribution:** Normal
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentiles:** 0.50, 0.75, 0.95, 0.99
*   **Iterations:** 1000 (Default). *Note: The script may be configured with fewer iterations (e.g., 50) for CI/sandbox testing environments.*

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
