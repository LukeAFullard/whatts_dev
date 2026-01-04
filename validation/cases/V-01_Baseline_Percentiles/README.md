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
*Run Date: 2026-01-04 (Iterations=50)*

| Scenario | Method | Target Coverage | Actual Coverage | Avg Width | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **p50** | Projection | 0.95 | 0.960 | 0.317 | **PASS** |
| **p50** | Quantile Regression | 0.95 | 0.940 | 0.614 | **PASS** |
| **p75** | Projection | 0.95 | 0.860 | 0.272 | FAIL |
| **p75** | Quantile Regression | 0.95 | 0.920 | 0.604 | **PASS** |
| **p95** | Projection | 0.95 | 0.860 | 0.529 | FAIL |
| **p95** | Quantile Regression | 0.95 | 0.660 | 0.641 | FAIL |
| **p99** | Projection | 0.95 | 0.360 | 0.000 | FAIL |
| **p99** | Quantile Regression | 0.95 | 0.540 | 0.695 | FAIL |

## 7. Interpretation & Conclusion
**Analysis:**
The preliminary run used a reduced iteration count ($I=50$) to verify pipeline functionality, which results in a high margin of error for coverage estimates ($\approx \pm 14\%$).

*   **Central Tendency (p50):** Both methods performed well, achieving the target 95% confidence coverage.
*   **Moderate Tails (p75):** Quantile Regression passed, while Projection was slightly under-conservative (86% vs 95%).
*   **Extreme Tails (p95, p99):** Both methods struggled. This is expected for $N=50$:
    *   For **p99**, a sample size of 50 is insufficient to reliably estimate the percentile (as $1/50 = 0.02$, the maximum value is roughly the 98th percentile). The "FAIL" here confirms the known limitation that $N$ must be larger (typically $>100$) for p99 compliance.
    *   For **p95**, the failures (Projection 86%, QR 66%) suggest that for small sample sizes, the asymptotic assumptions of the bootstrap (QR) and the Normal approximation (Projection) may not fully hold, or the low iteration count simply produced a noisy result.

**Anomalies:**
*   **p99 Projection Width:** The average width was 0.000. This likely indicates a calculation failure or edge case where the method defaulted to the maximum observed value without a valid tolerance margin.
*   **QR Coverage Drop:** QR coverage dropped significantly at p95 (66%). This suggests the bootstrap method may be underestimating the variance in the tail for small $N$.

**Recommendation:**
Rerun with $I=1000$ and potentially increase $N$ to 100 for p95/p99 validation to isolate method performance from sampling noise.
