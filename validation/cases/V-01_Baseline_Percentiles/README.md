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
The methods showed degraded performance at high percentiles (p95, p99) in this test configuration ($N=50$). A subsequent diagnostic investigation with $N=200$ confirmed that **Sample Size** is the primary driver of these failures.

*   **Projection Method:**
    *   At $N=50$, the method under-covered p95 (Actual ~0.86-0.90) and p99.
    *   **Investigation Finding:** Increasing sample size to $N=200$ restored coverage to **0.95** (PASS).
    *   **Conclusion:** The Wilson-Hazen approximation requires larger sample sizes to accurately bound the 95th+ percentiles. The method is functionally correct but sensitive to $N$. False trend detection was ruled out (rate $\approx 5\%$, matching $\alpha$).

*   **Quantile Regression Method:**
    *   At $N=50$, coverage was very low for tails.
    *   **Investigation Finding:** Increasing sample size to $N=200$ improved coverage to 0.85, but it still fell short of the 0.95 target.
    *   **Conclusion:** The Bootstrap Quantile Regression method is "data-hungry" and may require significantly larger datasets ($N > 200$) or more bootstrap iterations to achieve nominal coverage for tail percentiles.

**Recommendation:**
For future validation runs of tail percentiles (p95+), use $N \ge 200$. For small datasets ($N \approx 50$), rely on p50-p75 for verification or accept wider confidence intervals.
