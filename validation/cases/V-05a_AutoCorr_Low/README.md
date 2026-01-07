# Validation Case V-05a: Low Autocorrelation

## Objective
Verify the Effective Sample Size ($n_{eff}$) adjustments (Projection) and block bootstrapping (QR) for low autocorrelation ($\rho=0.3$).

## Data Generation Parameters
*   **Distribution**: Normal ($\mu=0, \sigma=1$)
*   **Autocorrelation**: AR(1) with $\rho=0.3$.
*   **Trend**: None.
*   **Target Percentile**: $p=0.95$.
*   **Sample Sizes**: $N \in \{30, 60, 100, 200\}$.

## Success Criteria
*   **Target Coverage**: 0.95.
