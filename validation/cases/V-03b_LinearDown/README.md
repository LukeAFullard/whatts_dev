# Validation Case V-03b: Linear Down Trend

## Objective
Ensure that trend detection and removal (Projection) or modeling (QR) works for monotonic decreasing trends.

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0 + \beta t, \sigma=1$)
*   **Trend**: Linear Decreasing ($-0.05 \sigma / t$)
*   **Autocorrelation**: $\rho=0$
*   **Target Percentile**: $p=0.95$
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$

## Success Criteria
*   **Target Coverage**: 0.95 (Two-Sided Interval)
*   **Pass Threshold**: Actual coverage within $\pm 0.03$ of target (0.92 - 0.98).

## Interpretation
Similar to V-03a, but testing that negative slopes are handled correctly and not treated as zero (or absolute errors).
