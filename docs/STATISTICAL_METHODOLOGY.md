# Statistical Methodology: Wilson-Hazen with Probit Interpolation and Chi-Square Correction

## 1. Overview

The `whatts` library employs a comprehensive, hybrid statistical workflow to calculate Upper Tolerance Limits (UTL) and Confidence Intervals for environmental compliance. This methodology is robust for small sample sizes ($N \approx 30-60$), non-normal distributions, and time-dependent data properties like trends and autocorrelation.

The end-to-end process consists of four key stages:
1.  **Trend Analysis & Projection:** Removing long-term trends to isolate the stochastic distribution and projecting results to a target date.
2.  **Effective Sample Size Adjustment:** Correcting for autocorrelation (serial dependence) to avoid overestimating the information content of the data.
3.  **Rank Calculation (Wilson-Hazen):** Determining the probability rank of the Tolerance Limit using the Wilson Score Interval, with conditional Chi-Square boundary corrections.
4.  **Value Estimation (Probit Interpolation):** Mapping the calculated rank to a physical value using Z-scores to handle tail curvature and extrapolation.

---

## 2. Step 1: Trend Analysis & Projection

Before statistical analysis, the data is assessed for monotonic trends. If a trend exists, the distribution is changing over time, so analyzing the raw data as a single static pool is invalid.

### 2.1 Trend Detection (Mann-Kendall)
The library uses the **Mann-Kendall Trend Test** to determine if a statistically significant monotonic trend exists.
*   **Significance Level ($\alpha$):** Defaults to `1 - confidence` (e.g., 0.05 for 95% confidence).
*   **Method:** The test evaluates whether data values consistently increase or decrease over time, irrespective of linearity.

### 2.2 Trend Magnitude (Sen's Slope)
If a trend is detected ($p < \alpha$), the magnitude is estimated using the **Theil-Sen Estimator** (median of all pairwise slopes). This is robust to outliers compared to Ordinary Least Squares (OLS).

$$ \text{Slope} = \text{Median}\left( \frac{x_j - x_i}{t_j - t_i} \right) \quad \text{for all } i < j $$

### 2.3 Projection (Detrending)
The data is "projected" to a common reference point (the **Target Date**, usually the current/end date) to form a stationary dataset for analysis.

$$ x_{projected, i} = x_i + \text{Slope} \times (t_{target} - t_i) $$

Where:
*   $x_i$: Original value at time $t_i$.
*   $t_{target}$: The target date (e.g., maximum date in series).
*   $x_{projected, i}$: The adjusted value representing what the observation would be if it occurred at the target date.

If no trend is detected, $x_{projected} = x_{raw}$.

---

## 3. Step 2: Effective Sample Size Adjustment

Environmental data often exhibits **autocorrelation** (measurements close in time are similar). This reduces the "effective" number of independent observations. Using the raw sample size $N$ would underestimate uncertainty (intervals would be too narrow).

### 3.1 Bayley & Hammersley Formula
We calculate the **Effective Sample Size ($N_{eff}$)** using the "Sum of Correlations" method:

$$ \frac{1}{N_{eff}} = \frac{1}{N} + \frac{2}{N^2} \sum_{k=1}^{N-1} (N - k) \rho_k $$

Or equivalently:
$$ N_{eff} = \frac{N}{1 + 2 \sum_{k=1}^{N_{cutoff}} \left(1 - \frac{k}{N}\right) \rho_k} $$

Where:
*   $\rho_k$ is the autocorrelation at lag $k$.
*   The summation typically stops when $\rho_k$ becomes non-positive.

This $N_{eff}$ is used in all subsequent variance and confidence interval calculations.

---

## 4. Step 3: Rank Calculation (Wilson-Hazen)

This step determines the **probability rank** (percentile) of the Tolerance Limit.
*   **Goal:** Find rank $p_{limit}$ such that we are $C\%$ confident the true target percentile lies within the bounds.
*   **Default:** Two-Sided Confidence Interval ($1 - \alpha$).
*   **Inputs:** Target Percentile $\hat{p}$, $N_{eff}$, Confidence Level.

### 4.1 Base Method: Wilson Score Interval
We calculate the Wilson Score Interval for the binomial proportion $\hat{p}$.
For a Two-Sided Interval with confidence $1 - \alpha$, we use $\alpha_{tail} = \alpha / 2$.

**Z-Score:**
$$ z = \Phi^{-1}(1 - \alpha_{tail}) $$

**Interval Calculation:**
$$ Center = \frac{\hat{p} + \frac{z^2}{2 N_{eff}}}{1 + \frac{z^2}{N_{eff}}} $$
$$ Margin = \frac{z}{1 + \frac{z^2}{N_{eff}}} \sqrt{ \frac{\hat{p}(1-\hat{p})}{N_{eff}} + \frac{z^2}{4 N_{eff}^2} } $$

$$ p_{lower} = Center - Margin $$
$$ p_{upper} = Center + Margin $$

### 4.2 Expanded Chi-Square Boundary Correction
The normal approximation used in the Wilson method degrades when $N_{eff}$ is small AND the percentile is near 0 or 1. `whatts` employs a hybrid switch to the exact Clopper-Pearson (Chi-Square) method in these cases.

**Trigger Logic (Symmetric):**
1.  **Distance from Top:** $D_{top} = N_{eff} \times (1 - \hat{p})$
2.  **Distance from Bottom:** $D_{bottom} = N_{eff} \times \hat{p}$
3.  **Thresholds:** Trigger if $N_{eff} \le 120$ AND $D \le 5.0$.

**Correction Formulas:**
If triggered for the Upper Limit:
$$ p_{upper} = 1.0 - \frac{1}{2 N_{eff}} \chi^2_{\alpha_{tail}, 2 D_{top}} $$

If triggered for the Lower Limit:
$$ p_{lower} = \frac{1}{2 N_{eff}} \chi^2_{\alpha_{tail}, 2 D_{bottom}} $$

---

## 5. Step 4: Value Estimation (Probit Interpolation)

The final step maps the calculated ranks ($p_{lower}, p_{upper}$) to physical values using the projected data distribution.

### 5.1 Sorting & Plotting Positions
The projected data $x_{proj}$ is sorted. Empirical probabilities are assigned using the **Hazen Plotting Position**:
$$ p_i = \frac{i - 0.5}{N} $$

### 5.2 Probit Transformation
Standard linear interpolation underestimates values on the curved tails of a distribution. We transform to **Z-space** (Standard Normal Quantiles) to linearize the relationship:

$$ Z_i = \Phi^{-1}(p_i) $$
$$ Z_{target} = \Phi^{-1}(p_{limit}) $$

### 5.3 Interpolation & Extrapolation
We perform linear interpolation in Z-space.

**Interpolation ($Z_{min} \le Z_{target} \le Z_{max}$):**
Find neighbors $i, i+1$ and interpolate linearly between $(Z_i, x_i)$ and $(Z_{i+1}, x_{i+1})$.

**Extrapolation ($Z_{target} > Z_{max}$):**
If the tolerance rank exceeds the maximum plotting position (common in small samples), we extrapolate using the slope of the tail (last two points):

$$ \text{Slope} = \frac{x_N - x_{N-1}}{Z_N - Z_{N-1}} $$
$$ UTL = x_N + \text{Slope} \times (Z_{target} - Z_N) $$

(Symmetric logic applies for the lower tail).

---

## 6. References

1.  **Hazen, A. (1914).** "Storage to be Provided in Impounding Reservoirs." *Transactions of the American Society of Civil Engineers*, 77, 1539-1640.
2.  **Clopper, C. J., & Pearson, E. S. (1934).** "The use of confidence or fiducial limits illustrated in the case of the binomial." *Biometrika*, 26(4), 404-413.
3.  **Brown, L. D., Cai, T. T., & DasGupta, A. (2001).** "Interval estimation for a binomial proportion." *Statistical Science*, 16(2), 101-133.
4.  **Helsel, D.R., and Hirsch, R.M. (2002).** *Statistical Methods in Water Resources*. U.S. Geological Survey, Techniques of Water-Resources Investigations, Book 4, Chapter A3. (Trend Analysis and Probability Plotting).
5.  **Bayley, G. V., & Hammersley, J. M. (1946).** "The effective number of independent observations in an autocorrelated time series." *Supplement to the Journal of the Royal Statistical Society*, 8(2), 184-197.
