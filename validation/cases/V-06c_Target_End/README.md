# Validation Case V-06: Target Date Sensitivity

## Objective
Verify that the system correctly projects tolerance limits to different points in time.

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0 + \beta t, \sigma=1$)
*   **Trend**: Linear Increasing ($0.05 \sigma / t$)
*   **Target Percentile**: $p=0.95$.
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$.

## Scenarios
*   **V-06a**: Project to Start ($t=0$).
*   **V-06b**: Project to Middle ($t=N/2$).
*   **V-06c**: Project to End ($t=N$).

## Success Criteria
*   **Target Coverage**: 0.95.
