# Code Audit Report: `whatts` Library

## 1. Executive Summary

A comprehensive deep code audit was performed on the `whatts` repository. The audit focused on statistical methodology, code correctness, defensibility for regulatory compliance, and potential bugs.

**Verdict:** The library is **Methodologically Defensible** and **Accurate**. The core statistical algorithms (Wilson-Hazen, Bayley & Hammersley $N_{eff}$, Sen's Slope) are implemented correctly and align with standard environmental statistics practices.

No critical bugs affecting the accuracy of compliance determinations were found. However, findings were identified regarding usability, consistency, and minor edge-case handling. Enhancements have been proposed and implemented to improve the "defensibility" of the output in a legal context.

## 2. Methodology Validation

The following statistical components were validated against standard literature and intended design:

| Component | Method | Validation Status | Notes |
| :--- | :--- | :--- | :--- |
| **Trend Projection** | Sen's Slope & Mann-Kendall | **VALID** | Uses `MannKS` library. Verified correct handling of timestamps (seconds) and projection logic. |
| **Effective Sample Size** | Bayley & Hammersley (Sum of Correlations) | **VALID** | Correctly implements the lag-sum formula. Explicitly handles zero-variance (constant) data by setting $N_{eff}=1.0$. |
| **Upper Tolerance Limit** | Wilson Score Interval (One-Sided) | **VALID** | Correctly uses $Z_{1-\alpha}$ (not $Z_{1-\alpha/2}$). Correctly applies $N_{eff}$ to variance and center calculations. |
| **Boundary Correction** | Chi-Square Adjustment | **VALID** | Implements a lower-bound on failure counts using Chi-Square inverse CDF, providing a tighter but safe bound for small sample sizes near perfect compliance. |
| **Percentile Estimation** | Hazen Plotting Position | **VALID** | Standard interpolation method for environmental data. |

## 3. Findings & Observations

### 3.1. Critical Issues
*None found.*

### 3.2. Minor Issues & Enhancements

#### A. Slope Unit Readability (Usability)
*   **Observation:** The library internally calculates and returns trend slopes in **units per second** (e.g., `1.15e-05 mg/L/s`).
*   **Impact:** This number is difficult for stakeholders or courts to interpret ("Is this trend significant? It looks like zero.").
*   **Remediation:** Added `trend_slope_per_year` to the output, converting the slope to **units per year** (assuming 365.25 days/year) for clearer reporting.

#### B. Confidence Level Consistency (Methodology)
*   **Observation:** The trend detection step (`MannKS`) was hardcoded to use `alpha=0.05` (95% confidence), even if the user requested a different confidence level for the Tolerance Limit (e.g., 99%).
*   **Impact:** Inconsistent statistical rigor. A 99% UTL should ideally rely on a trend detected at 99% confidence (or similar user-defined threshold).
*   **Remediation:** Updated the code to propagate the user's `confidence` parameter to the trend detection step.

#### C. Autocorrelation on Gapped Data (Limitation)
*   **Observation:** `calculate_neff_sum_corr` operates on the data vector after dropping NaNs, effectively treating non-contiguous data as contiguous.
*   **Impact:** May slightly overestimate correlation if large gaps exist.
*   **Defensibility:** This is a documented design choice to enable $N_{eff}$ calculation on sparse datasets. Given the conservative nature of the Bayley & Hammersley method, this is acceptable but should be noted in detailed technical reports.

#### D. Sample Size Limits (Safety)
*   **Observation:** The external `MannKS` library may fail for extremely small sample sizes ($N < 5$) due to insufficient data for confidence interval calculations.
*   **Remediation:** The library enforces input validation.
    *   **Error:** Raises `ValueError` if $N < 5$ (Unsafe).
    *   **Warning:** Issues `UserWarning` if $5 \le N < 10$ (Statistically weak but computationally safe).
    *   This "vaccinates" the application against external library crashes.

## 4. Code Quality & Safety
*   **Input Validation:** Robust checks for sample size.
*   **Edge Cases:**
    *   **Constant Data:** Handled safely ($N_{eff}=1$).
    *   **Perfect Compliance:** Handled safely (UTL clamped to 1.0).
    *   **Negative Projections:** Clamped to 0.0 (physically realistic).
*   **Dependencies:** Proper use of `numpy`, `scipy`, and `mannks`.

## 5. Conclusion
The `whatts` library is suitable for regulatory use. The implemented fixes for slope units and alpha consistency further enhance its transparency and defensibility.
