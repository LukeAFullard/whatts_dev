# Validation Case: V-01c_p95

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the High Percentile (p95) for a standard normal distribution with no trend and no autocorrelation.

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
*   **Target Percentile:** 0.95
*   **Iterations:** 200 (Reduced from 1000 for performance)

## 4. Methodology
**Execution Strategy:**
This folder contains multiple scripts to test different sample sizes and methods independently to avoid timeouts.
1.  Generate standard normal data.
2.  Apply `whatts` methods (Projection and Quantile Regression).
3.  Calculate **Actual Coverage**: The proportion of simulations where the true underlying percentile falls within the calculated Two-Sided 95% Confidence Interval (LTL $\le$ True $\le$ UTL).
4.  Compare against **Target Coverage** (0.95).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (0.95).

*   **PASS:** $|Actual - 0.95| \le 0.03$ (i.e., 0.92 to 0.98)
*   **FAIL:** $|Actual - 0.95| > 0.03$

## 6. Results Summary
Results are appended to `validation/master_results.csv`.

| Method | N | Target | Actual Coverage | Avg Width | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Projection** | 30 | 0.95 | 0.9000 | 1.93 | FAIL |
| **Projection** | 60 | 0.95 | 0.9400 | 1.27 | PASS |
| **Projection** | 100 | 0.95 | 0.9300 | 0.89 | PASS |
| **Projection** | 200 | 0.95 | 0.9050 | 0.60 | FAIL |
| **Quantile Regression** | 30 | 0.95 | 0.8300 | 2.71 | FAIL |
| **Quantile Regression** | 60 | 0.95 | 0.9200 | 2.08 | PASS |
| **Quantile Regression** | 100 | 0.95 | 0.9050 | 1.58 | FAIL |
| **Quantile Regression** | 200 | 0.95 | 0.9250 | 1.22 | PASS |

## 7. Interpretation & Conclusion
**Analysis:**
The validation checked the **Interval Coverage** (target 95%). Both methods show some inconsistency, particularly at small and very large sample sizes for the high 95th percentile.
*   **Projection (Wilson-Hazen):** Performs reasonably well for mid-sized samples (N=60, N=100) with passing coverage. However, it under-covers at N=30 (0.90) and surprisingly at N=200 (0.905).
*   **Quantile Regression:** Shows significant under-coverage at N=30 (0.83). It passes at N=60 and N=200, but fails at N=100 (0.905).

**Anomalies:**
The failure at N=200 for Projection and N=100 for QR suggests the methods might be slightly anti-conservative for high percentiles even as N increases, or that 200 iterations is insufficient to smooth out stochastic noise (±3% tolerance is tight). The oscillation between PASS and FAIL across N indicates variability.
