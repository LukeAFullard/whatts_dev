# Validation Case: V-01b_p75

## 1. Objective
**What is being tested:**
Verify that both methods correctly estimate the Upper Quartile (p75) for a standard normal distribution with no trend and no autocorrelation across various sample sizes.

**Category:**
Baseline Performance

## 2. Rationale
**Why this test is important:**
Baseline accuracy is fundamental. We need to ensure that in the simplest case (normal, i.i.d.), the methods provide correct coverage for various percentiles, especially tails, and how this performance scales with sample size.

## 3. Data Generation Parameters
**Configuration:**
*   **Sample Size ($N$):** 30, 60, 100, 200
*   **Distribution:** Standard Normal
*   **Trend:** None
*   **Autocorrelation ($\rho$):** 0.0
*   **Target Percentile:** 0.75
*   **Iterations:** 200 (Reduced from 1000 for speed)

## 4. Methodology
**Execution Strategy:**
This test runs a Monte Carlo simulation using the script in this folder (`run_test.py`).
1.  Generate synthetic data based on the parameters above.
2.  Apply `whatts` methods:
    *   **Projection:** Wilson-Hazen with Detrending.
    *   **Quantile Regression:** Moving Block Bootstrap.
3.  Calculate **Actual Coverage**: The proportion of simulations where the **Interval [LTL, UTL]** contains the true underlying percentile.
4.  Compare against **Target Coverage** (confidence level = 0.95).

## 5. Success Criteria
**Pass/Fail Definition:**
A method passes if the **Actual Coverage** is within **±3%** of the **Target Coverage** (0.95).

*   **PASS:** $|Actual - 0.95| \le 0.03$ (0.92 to 0.98)
*   **FAIL:** $|Actual - 0.95| > 0.03$

## 6. Results Summary
*Note: These results are automatically appended to `validation/master_results.csv`.*

| N | Method | Iterations | Target Coverage | Actual Coverage | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 30 | **Projection** | 200 | 0.95 | 0.8950 | FAIL |
| 30 | **Quantile Regression** | 200 | 0.95 | 0.9100 | FAIL |
| 60 | **Projection** | 200 | 0.95 | 0.9100 | FAIL |
| 60 | **Quantile Regression** | 200 | 0.95 | 0.9250 | PASS |
| 100 | **Projection** | 200 | 0.95 | 0.9500 | PASS |
| 100 | **Quantile Regression** | 200 | 0.95 | 0.9400 | PASS |
| 200 | **Projection** | 200 | 0.95 | 0.9350 | PASS |
| 200 | **Quantile Regression** | 200 | 0.95 | 0.9600 | PASS |

## 7. Interpretation & Conclusion
**Analysis:**
*   **Sample Size Sensitivity**: Both methods struggle with coverage at small sample sizes ($N=30$) for the 75th percentile.
    *   **Projection**: Exhibits consistent under-coverage at N=30 and N=60, only reaching the target zone at N=100.
    *   **Quantile Regression**: Fails marginally at N=30 (0.91 vs 0.92 threshold) but passes from N=60 onwards.

**Anomalies:**
*   QR at N=30 failed with 0.9100, which is just below the 0.9200 cutoff.
*   Projection at N=200 (0.9350) is a borderline PASS (within +/- 3%). It suggests the method remains slightly optimistic even at larger N.
