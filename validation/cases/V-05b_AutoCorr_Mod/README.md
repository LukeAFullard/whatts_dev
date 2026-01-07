# Validation Case V-05b: Moderate Autocorrelation

## Objective
Verify performance for moderate autocorrelation ($\rho=0.6$).

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0, \sigma=1$)
*   **Autocorrelation**: AR(1) with $\rho=0.6$.
*   **Trend**: None.
*   **Target Percentile**: $p=0.95$.
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$.

## Success Criteria
*   **Target Coverage**: 0.95.
