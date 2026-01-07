# Validation Case V-03a: Linear Up Trend

## Objective
Ensure that trend detection and removal (Projection) or modeling (QR) works for monotonic increasing trends.

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0 + \beta t, \sigma=1$)
*   **Trend**: Linear Increasing ($0.05 \sigma / t$)
*   **Autocorrelation**: $\rho=0$
*   **Target Percentile**: $p=0.95$
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$

## Success Criteria
*   **Target Coverage**: 0.95 (Two-Sided Interval)
*   **Pass Threshold**: Actual coverage within $\pm 0.03$ of target (0.92 - 0.98).

## Interpretation
The "Projection" method should detect the significant trend, detrend the data, calculate limits on residuals, and re-project to the end.
The "Quantile Regression" method should model the 95th percentile slope directly.
