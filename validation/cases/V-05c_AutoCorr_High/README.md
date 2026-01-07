# Validation Case V-05c: High Autocorrelation

## Objective
Verify performance for high autocorrelation ($\rho=0.8$).

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0, \sigma=1$)
*   **Autocorrelation**: AR(1) with $\rho=0.8$.
*   **Trend**: None.
*   **Target Percentile**: $p=0.95$.
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$.

## Success Criteria
*   **Target Coverage**: 0.95.
