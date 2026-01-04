# Statistical Methodology: Wilson-Hazen with Probit Interpolation and Chi-Square Correction

## 1. Overview

The `whatts` library employs a hybrid statistical approach to calculate Upper Tolerance Limits (UTL) for environmental compliance. This methodology is designed to be robust for small sample sizes ($N \approx 30-60$) and non-normal distributions, while maintaining statistical defensibility.

The core algorithm consists of three components:
1.  **Wilson-Hazen Base Method:** Using Hazen plotting positions and the Wilson Score Interval to determine the tolerance rank.
2.  **Expanded Chi-Square Boundary Correction:** A transition to the exact Clopper-Pearson (Chi-Square) method when sample sizes are small and the target percentile is near the upper boundary.
3.  **Probit (Z-Score) Interpolation:** Mapping the calculated rank to a data value using Normal Quantiles to handle tail curvature and enable extrapolation.

---

## 2. Wilson-Hazen Base Method

### 2.1 Concept
Instead of assuming the data follows a specific parametric distribution (like Normal or Gamma), the method operates on **ranks**. It asks: *"Given $N$ observations, what is the probability rank $p_{upper}$ such that we are 95% confident the true $p$-th percentile is below $p_{upper}$?"*

### 2.2 Formulation
For a target percentile $\hat{p}$ (e.g., 0.95), sample size $N$, and Effective Sample Size $N_{eff}$ (adjusted for autocorrelation), the one-sided Upper Wilson Score Limit is calculated as:

$$
center = \frac{\hat{p} + \frac{z^2}{2 N_{eff}}}{1 + \frac{z^2}{N_{eff}}}
$$

$$
margin = \frac{z}{1 + \frac{z^2}{N_{eff}}} \sqrt{ \frac{\hat{p}(1-\hat{p})}{N_{eff}} + \frac{z^2}{4 N_{eff}^2} }
$$

$$ p_{upper} = center + margin $$

Where $z = \Phi^{-1}(1 - \alpha)$ is the Z-score for the desired confidence level (e.g., 1.645 for 95% confidence).

---

## 3. Expanded Chi-Square Boundary Correction

### 3.1 The Problem
The Wilson Score Interval relies on a normal approximation to the binomial distribution. This approximation degrades when:
1.  Sample size is small ($N_{eff} \le 120$).
2.  The target percentile is close to 1.0 (the boundary).

In these cases, the standard Wilson method can be **non-conservative** (underestimating the upper limit).

### 3.2 The Solution
`whatts` switches to a correction derived from the exact Clopper-Pearson interval (using the Chi-Square distribution) when the "Distance from Top" is small.

**Distance Calculation:**
$$ D_{top} = N_{eff} \times (1 - \hat{p}) $$
This represents the expected number of observations above the percentile.

**Trigger Conditions (Configurable):**
The correction is applied if:
*   $N_{eff} \le \text{Medium Threshold}$ (default 120) **AND**
*   $D_{top} \le \text{Distance Threshold}$ (default 5.0)

### 3.3 The Formula
When triggered, the corrected upper rank is:

$$ p_{upper} = 1.0 - \frac{1}{2 N_{eff}} \chi^2_{\alpha, 2 D_{top}} $$

Where $\chi^2_{\alpha, \nu}$ is the quantile function of the Chi-Square distribution with $\nu$ degrees of freedom. This provides a rigorous, conservative upper bound.

---

## 4. Probit (Z-Score) Interpolation

### 4.1 The Challenge
Once $p_{upper}$ is determined, it must be mapped to a physical value (concentration, etc.). Standard linear interpolation between data points is flawed for tail estimation because:
1.  **Curvature:** Probability distributions are curved (sigmoidal) in the tails. Linear interpolation underestimates values on convex tails.
2.  **Extrapolation:** $p_{upper}$ often exceeds the maximum plotting position of the data ($p_{max} \approx 1 - 0.5/N$). Linear interpolation cannot estimate values beyond the maximum data point.

### 4.2 The Method
`whatts` uses **Probit Interpolation**:
1.  **Plotting Positions:** Assign Hazen ranks to sorted data: $p_i = (i - 0.5) / N$.
2.  **Transformation:** Convert ranks to Z-scores: $Z_i = \Phi^{-1}(p_i)$.
3.  **Target Z:** Convert target rank to $Z_{target} = \Phi^{-1}(p_{upper})$.
4.  **Interpolation:** Linearly interpolate $Z_{target}$ between observed $Z_i$ values to find the corresponding data value.

### 4.3 Extrapolation Logic
If $Z_{target} > Z_{max}$ (the Z-score of the largest data point), the method extrapolates using the slope of the tail:

$$ slope = \frac{x_{(n)} - x_{(n-1)}}{Z_{(n)} - Z_{(n-1)}} $$

$$ UTL = x_{(n)} + slope \times (Z_{target} - Z_{(n)}) $$

This effectively projects the "trajectory" of the distribution tail into the unobserved region, assuming a local lognormal/normal shape.

---

## 5. References

1.  **Hazen, A. (1914).** "Storage to be Provided in Impounding Reservoirs." *Transactions of the American Society of Civil Engineers*, 77, 1539-1640.
2.  **Clopper, C. J., & Pearson, E. S. (1934).** "The use of confidence or fiducial limits illustrated in the case of the binomial." *Biometrika*, 26(4), 404-413.
3.  **Brown, L. D., Cai, T. T., & DasGupta, A. (2001).** "Interval estimation for a binomial proportion." *Statistical Science*, 16(2), 101-133.
4.  **Helsel, D.R., and Hirsch, R.M. (2002).** *Statistical Methods in Water Resources*. U.S. Geological Survey, Techniques of Water-Resources Investigations, Book 4, Chapter A3. (Discussion on Probability Plotting and ROS).
