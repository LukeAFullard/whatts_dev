# Statistical Frameworks for Environmental Compliance: An Exhaustive Evaluation of the Wilson-Hazen Method and Adaptations for Time-Series Dynamics

## Executive Summary

The assessment of freshwater attribute states for regulatory compliance, particularly under frameworks such as the National Policy Statement for Freshwater Management (NPS-FM) 2020, necessitates a rigorous statistical approach to estimate summary statistics like the 95th percentile. These statistics serve as critical thresholds for determining whether water bodies meet national bottom lines or target attribute states (TAS). However, the estimation of these parameters from finite monitoring data is subject to inherent uncertainty arising from two distinct sources: sampling error and natural environmental variability.1

The "Wilson-Hazen" method has emerged as a standard practice among regional councils for calculating these percentiles and their associated confidence intervals. This method combines the Hazen plotting position for unbiased point estimation of percentiles with the Wilson Score Interval for quantifying the uncertainty of the underlying binomial proportion. For independent and identically distributed (i.i.d.) data, this approach represents a significant advancement over traditional methods like the Wald interval, particularly for handling skewed distributions and extreme percentiles common in water quality data (e.g., E. coli, sediment).2

However, environmental monitoring data rarely satisfy the assumption of independence. They are characterized by serial correlation (autocorrelation) and non-stationarity (trends and seasonality). This report finds that applying the standard Wilson-Hazen method to autocorrelated time series results in a systematic underestimation of variance. This leads to confidence intervals that are artificially narrow, inflating the effective sample size and increasing the risk of Type I errors—falsely concluding a site is compliant or stable when it is not. Furthermore, the presence of monotonic trends or long-term climatic cycles (e.g., ENSO) renders the concept of a static "baseline" percentile methodologically fraught without adjustment.1

To reconcile the statistical robustness of the Wilson-Hazen method with the realities of time-series data, this report recommends a stratified approach to modification. The primary recommendation is the integration of an Effective Sample Size ($n_{eff}$) adjustment into the Wilson Score formula. This adjustment utilizes autocorrelation functions (ACF) or variance inflation factors (VIF) to down-weight redundant observations, thereby widening the confidence intervals to accurately reflect the true information content of the data.6 For data exhibiting complex dependency structures or non-normality, Block Bootstrapping offers a non-parametric alternative that preserves serial dependence during resampling.9 Finally, in the presence of trends, Quantile Regression is identified as the superior method for estimating current attribute states, as it models the changing distribution directly rather than relying on a potentially obsolete historical average.11

## 1. Introduction: The Intersection of Regulatory Policy and Statistical Science

### 1.1 The Regulatory Imperative: National Policy Statement for Freshwater Management

The management of freshwater resources is increasingly driven by quantitative targets. Under the NPS-FM 2020, regional councils are mandated to identify "baseline states" for a suite of mandatory attributes—ranging from dissolved oxygen and nitrate toxicity to E. coli and visual clarity.1 These baselines are not merely descriptive; they form the legal benchmark against which future "target attribute states" (TAS) are set. The policy directive is clear: water quality must be at least maintained, and where degraded, improved. Consequently, the statistical precision with which these baselines are estimated has profound implications for resource consent limits, land-use planning, and infrastructure investment.1

Compliance is frequently assessed using summary statistics that describe the distribution of a pollutant over a specific assessment period—typically five years of monthly sampling. While medians are used for chronic toxicity (e.g., nitrate), upper percentiles (e.g., 95th percentile) are critical for acute risks (e.g., E. coli limits for human health). Clause 3.10(4) of the NPS-FM explicitly allows for these attribute states to be expressed in a way that "accounts for natural variability and sampling error".1 This clause acknowledges that a single number—a point estimate—confers a false sense of precision. A calculated 95th percentile of 540 E. coli/100mL might technically exceed a threshold of 500, but if the 95% confidence interval is $[480, 610]$, the exceedance is statistically uncertain.

### 1.2 The Role of the Wilson-Hazen Method

To operationalize this requirement, councils have adopted the "Wilson-Hazen" method. This nomenclature refers to a specific pairing of statistical techniques:

* **Hazen Plotting Position**: A method for assigning a cumulative probability or "rank" to each data point in a sorted sample, used to interpolate the specific value of the percentile.13
* **Wilson Score Interval**: A method for calculating the confidence interval around the proportion associated with that percentile (e.g., the proportion 0.95), which is then mapped back to the measured values.3

This combination is favored because it addresses specific challenges in water quality data. Environmental datasets are often small ($n < 60$ for a 5-year monthly record), highly skewed (log-normal or gamma distributions), and bounded (concentrations cannot be negative). Traditional methods often fail under these conditions; the Wilson-Hazen approach is robust to skew and respects boundaries.3

### 1.3 The Core Problem: Time-Series Limitations

The theoretical validity of the Wilson-Hazen method relies on the assumption that the $n$ observations in the dataset are independent and identically distributed (i.i.d.). This assumption implies that measuring the water quality today gives no information about the water quality tomorrow, other than what is contained in the global mean and variance.

This assumption is demonstrably false for environmental monitoring. River flows, nutrient concentrations, and biological indices exhibit autocorrelation (serial dependence) and non-stationarity (trends and cycles).1

* **Autocorrelation**: High flows today usually mean high flows tomorrow. This persistence means that a sample of 60 monthly measurements may only contain the information equivalent of 30 or 40 independent samples. Treating them as 60 independent points underestimates the standard error.
* **Trends**: If a river is improving due to fencing and riparian planting, the mean and variance are changing over time. A 5-year percentile creates a "smear" of the old, degraded state and the new, improved state, failing to represent the true current condition.1

This report aims to deconstruct the Wilson-Hazen method to validate its general appropriateness and then rigorously derive the necessary modifications—specifically regarding effective sample size and trend analysis—to ensure it remains a valid tool for regulatory compliance in the face of time-series dynamics.

## 2. General Appropriateness of the Wilson-Hazen Method

Before addressing the complexities of time series, it is essential to establish why the Wilson-Hazen method is the preferred baseline approach for independent data. Its selection is not arbitrary but rooted in specific statistical properties that make it superior to common alternatives like the Wald interval or Weibull plotting positions for environmental applications.

### 2.1 The Point Estimator: Hazen Plotting Position

Estimating a percentile (or quantile) from a finite sample is fundamentally a problem of assigning a rank or "plotting position" to ordered data. Let $X_{(1)} \le X_{(2)} \le \dots \le X_{(n)}$ be the ordered sample of $n$ observations. The $p$-th percentile is the value below which $p\%$ of the distribution lies.

There is no single solution for determining which sample value corresponds to a specific percentile. Instead, a family of estimators exists, generally described by the formula:

$$p_i = \frac{i - \alpha}{n - 2\alpha + 1}$$

where $i$ is the rank, $n$ is the sample size, and $\alpha$ is a constant parameter.16

#### 2.1.1 Why Hazen?

The Hazen plotting position sets $\alpha = 0.5$, yielding:

$$p_i = \frac{i - 0.5}{n}$$

This formula effectively centers the probability mass of each observation within its interval ($1/n$).

* **Neutrality**: Unlike the Weibull formula ($\alpha=0$, $p_i = i/(n+1)$), which is unbiased for the mean of the order statistic but biased for the median, the Hazen estimator is often considered a "middle-of-the-road" or continuity-corrected estimator.13
* **Symmetry**: It treats the tails of the distribution symmetrically. For example, with $n=10$, the lowest value is the 5th percentile ($0.5/10$) and the highest is the 95th percentile ($9.5/10$).
* **Regulatory Precedent**: The New Zealand Ministry for the Environment (MfE) and other international bodies have explicitly recommended Hazen for water quality percentile assessment.13 This standardization is crucial for comparability across regions.
* **Appropriateness**: For environmental data, where the true underlying distribution (e.g., log-normal, Gamma, Weibull) is often unknown or varies between sites, the Hazen method provides a non-parametric, robust point estimate that avoids the excessive bias at the tails seen in other methods.16

### 2.2 The Uncertainty Estimator: Wilson Score Interval

Calculating a confidence interval for a percentile is statistically equivalent to calculating a confidence interval for a binomial proportion. If we want the 95th percentile, we are effectively estimating the value $X$ such that the proportion of the population $\le X$ is $0.95$.

#### 2.2.1 The Failure of the Wald Interval

The most common method taught in introductory statistics is the Wald interval:

$$\hat{p} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}$$

While simple, the Wald interval relies on the normal approximation of the binomial distribution. This approximation collapses under the conditions typical of environmental compliance 3:

* **Boundary Violation**: For high percentiles (e.g., 99th) and small $n$, the upper bound of the Wald interval can exceed 1.0 (or 100%), which is physically impossible for a probability.
* **Zero Width**: If a sample has zero exceedances of a threshold (e.g., all samples are compliant), $\hat{p}=1$. The standard error becomes zero, calculating a confidence interval of $[1, 1]$. This falsely implies absolute certainty, whereas in reality, a small sample size still carries significant risk that the true rate is less than 1.4
* **Coverage Probability**: The actual coverage probability of Wald intervals is often significantly lower than the nominal level (e.g., a "95%" interval might only contain the true value 80% of the time) when $p$ is close to 0 or 1.4

#### 2.2.2 The Superiority of the Wilson Interval

The Wilson Score Interval solves these problems by inverting the score test for the proportion. Instead of assuming the standard error is defined by the sample proportion $\hat{p}$, it solves for the set of population proportions $p$ that would not be rejected by a hypothesis test given the data.

The interval is the solution to the quadratic inequality:

$$\left| \frac{\hat{p} - p}{\sqrt{p(1-p)/n}} \right| \le z$$

This yields the formula:

$$\tilde{p} = \frac{\hat{p} + \frac{z^2}{2n}}{1 + \frac{z^2}{n}} \pm \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}$$

Key Advantages for Regulation:

* **Asymmetry**: The interval is asymmetric, pulling towards 0.5. For a 95th percentile estimate, the lower bound will be further from the point estimate than the upper bound, accurately reflecting that the distribution is "cramped" against the 100% boundary.3
* **Boundary Respect**: The interval never exceeds $[0, 1]$.
* **Small Sample Performance**: It performs exceptionally well even for very small $n$ (e.g., $n=10$) or when $\hat{p}=0$ or $\hat{p}=1$. In the zero-exceedance case, it produces a valid one-sided interval, correctly identifying that there is still a probability of non-compliance compatible with the data.14

### 2.3 Synthesis: Why Wilson-Hazen is the Correct Baseline

The combination of Hazen (for unbiased point estimation) and Wilson (for robust uncertainty estimation) constitutes a "best-in-class" frequentist approach for environmental statistics under the assumption of independence.

The workflow is robust:

1. **Estimate**: Calculate the 95th percentile rank using Hazen: $R = 0.95n + 0.5$. Interpolate the data value.
2. **Interval**: Calculate the Wilson interval for $p=0.95$ and sample size $n$. This gives a lower proportion $p_{low}$ and upper proportion $p_{high}$.
3. **Map**: Convert these proportions to ranks ($R_{low} = p_{low} \times n$, $R_{high} = p_{high} \times n$) and interpolate the corresponding concentration values from the sorted data.

This method correctly handles the skew and bounded nature of compliance data. However, its reliance on $n$—the raw sample count—is its Achilles' heel when applied to time series.

## 3. The Theoretical Impact of Time-Series Limitations

The "appropriateness" of Wilson-Hazen degrades when the underlying statistical assumptions—specifically independence and stationarity—are violated by the physical reality of environmental systems.

### 3.1 The Mechanics of Autocorrelation (Serial Correlation)

Time series data in hydrology and water quality are almost essentially autocorrelated. This means the value of a variable at time $t$ ($X_t$) is correlated with the value at time $t-k$ ($X_{t-k}$).

* **Physical Origin**: Contaminants do not appear and disappear instantly. Groundwater lag times, sediment resuspension, and persistent weather patterns create "memory" in the system.1
* **Statistical Consequence**: If data are positively autocorrelated, a sample of $n$ observations contains less information than $n$ independent observations. The data points are somewhat redundant. For example, if today's nitrate level is high, knowing that tomorrow's is also high adds very little new information about the long-term average.21

**Impact on Wilson-Hazen**:

* The Wilson Score formula uses $n$ in the denominator of the variance term: $\sqrt{p(1-p)/n}$.
* When autocorrelation is present ($\rho > 0$), the true variance of the sample proportion is inflated by a factor related to the correlation.
* By using the unadjusted $n$, the Wilson formula underestimates the variance.

**Result**: The calculated confidence intervals are too narrow.

**Regulatory Implication**: This creates false precision. A regulator might conclude with "95% confidence" that a site meets a standard, when the true confidence is perhaps only 80% or lower. The risk of Type I error (incorrectly finding compliance) is significantly increased.23

### 3.2 The Mechanics of Non-Stationarity (Trends and Cycles)

Stationarity is the property that the statistical moments of the series (mean, variance) do not depend on time. The NPS-FM context explicitly involves assessing improvements (trends) or degradations.1

* **Trends**: If a river is subject to a restoration plan, nutrient levels may be trending downward. A "baseline state" calculated as a percentile over 5 years treats the data as a single static distribution.
* **Cycles**: Climate drivers like the Southern Oscillation Index (SOI) create multi-year cycles. A 5-year assessment period might purely by chance align with a La Niña phase (wet, high flushing) or an El Niño phase (dry, accrual).

**Impact on Wilson-Hazen**:

* **Distributional Mixing**: Calculating a single percentile on a trending dataset mixes data from the "high" past and "low" present. The resulting frequency distribution is platykurtic (flatter), leading to an overestimation of variance in some contexts, or simply a meaningless parameter that represents neither the past nor the present.1
* **Baseline Bias**: As noted in the NIWA report 1, if the assessment period ($n$ years) is shorter than the natural climate cycle, the estimated "baseline" is biased by the phase of the cycle. A baseline set during a drought will be fundamentally different from one set during a wet period, purely due to natural variability, not management. Wilson-Hazen provides a confidence interval around this biased estimate, effectively putting "error bars on a mistake."

## 4. Modifications for Autocorrelation: The Effective Sample Size Approach

To rescue the Wilson-Hazen method for time series, we must adjust the value of $n$ used in the calculation. We replace the raw sample size $n$ with the Effective Sample Size ($n_{eff}$). This quantity represents the number of independent observations that would provide the same statistical precision as the actual autocorrelated sample.

### 4.1 Theoretical Basis of Effective Sample Size

The variance of the sample mean (and analogously, proportions) for a time series is given by:

$$\text{Var}(\bar{X}) = \frac{\sigma^2}{n} \times \text{VIF}$$

where VIF is the Variance Inflation Factor.25 The VIF summarizes the impact of autocorrelation. The effective sample size is defined as:

$$n_{eff} = \frac{n}{\text{VIF}}$$

If correlation is positive, VIF $> 1$, and $n_{eff} < n$.

### 4.2 Calculating $n_{eff}$ for Wilson-Hazen

There are several methods to estimate $n_{eff}$, ranging from simple approximations to rigorous spectral density estimations.

#### 4.2.1 AR(1) Approximation

For many environmental time series, a first-order autoregressive process (AR(1)) is a sufficient approximation. In this model, the correlation decays exponentially with lag ($k$). The formula for $n_{eff}$ is:

$$n_{eff} \approx n \frac{1 - \rho_1}{1 + \rho_1}$$

where $\rho_1$ is the lag-1 autocorrelation coefficient.7

* **Application**: Calculate the correlation between the data $X_t$ and $X_{t-1}$. Plug this $\rho_1$ into the formula.
* **Example**: If $n=60$ (monthly samples, 5 years) and $\rho_1 = 0.5$:

$$n_{eff} = 60 \times \frac{0.5}{1.5} = 20$$

The 60 samples effectively provide only 20 independent data points. The confidence interval calculated with $n=20$ will be $\sqrt{3} \approx 1.73$ times wider than the one calculated with $n=60$.

#### 4.2.2 Sum of Correlations (General Method)

For more complex dependence structures (e.g., higher-order AR processes), $n_{eff}$ uses the sum of autocorrelations at all significant lags:

$$n_{eff} = \frac{n}{1 + 2 \sum_{k=1}^{\infty} \rho_k}$$

Practically, the summation is truncated when $\rho_k$ becomes statistically insignificant or negative.8 This method is more robust if the dependence extends beyond a single time step.

#### 4.2.3 The Korn and Graubard Adjustment

A specific refinement for binomial proportions (like percentiles) in complex survey data—which shares mathematical properties with clustered/autocorrelated data—is proposed by Korn and Graubard (1998).6

This method is highly relevant because it addresses the instability of variance estimates when sample sizes are small—a common issue in regulatory monitoring.

The Korn and Graubard adjusted effective sample size ($n_{eff}^*$) often incorporates a degrees-of-freedom adjustment using the $t$-distribution rather than the normal distribution.

* **Formula logic**: It penalizes the effective sample size further to account for the uncertainty in estimating the design effect (VIF) itself.
* **Implementation**: Instead of simply using $n_{eff}$ in the Wilson formula, one uses $n_{eff}^*$ and often modifies the interval construction to resemble a Clopper-Pearson (exact) interval scaled by this effective size. This is the "gold standard" for defensibility when $n$ is small and data are highly structured.18

### 4.3 Alternative: Block Bootstrapping

When the autocorrelation structure is unknown or difficult to model parametrically (e.g., non-linear dependence), Block Bootstrapping is a powerful non-parametric alternative.9

#### 4.3.1 Methodology

Standard bootstrapping resamples individual data points with replacement, which destroys the time-series structure. Block bootstrapping resamples blocks of contiguous data.

1. **Block Size ($l$)**: Choose a block size that captures the span of dependence. For monthly water quality data with seasonal dependence, a block size of $l=12$ (one year) or $l=6$ is common.
2. **Resampling**: Randomly draw blocks with replacement and stitch them together to form a new synthetic time series of length $n$.
3. **Estimation**: Calculate the 95th percentile (using Hazen) for this synthetic series.
4. **Iteration**: Repeat 10,000 times to build a distribution of the percentile.
5. **Interval**: The 2.5th and 97.5th percentiles of this bootstrap distribution form the 95% confidence interval.

**Advantages**:

* **Preserves Dependency**: By keeping blocks intact, the internal autocorrelation of the data is preserved in the resampled datasets.
* **Non-Normality**: It automatically handles the skewed nature of the data without assuming a specific distribution.34
* **Robustness**: Research suggests that for series lengths typical in ecosystem reporting ($n \approx 30-60$), block bootstrapping often provides more accurate coverage probabilities than analytical adjustments like $n_{eff}$ if the correlation structure is complex.35

## 5. Modifications for Trends: Addressing Non-Stationarity

When the "limitations" of the data include trending behavior (as pointed out in the user's scenario), calculating a single percentile for the entire period is methodologically flawed. The "baseline state" is a moving target.

### 5.1 The Problem with Static Percentiles

If a river's nitrogen concentration is trending downwards at 5% per year, the "95th percentile over the last 5 years" is a descriptive statistic of the history, not an estimate of the current state. It will be biased upwards by the high values from 4-5 years ago. Conversely, a degrading river will have a baseline that looks too optimistic.

### 5.2 Method 1: Detrending and Residual Analysis

To estimate the variability of the site correctly while accounting for the trend:

1. **Model the Trend**: Fit a robust trend line (e.g., Theil-Sen estimator or Seasonal Kendall) to the data: $Y_t = \text{Trend}_t + S_t + \epsilon_t$ (where $S_t$ is seasonality).
2. **Extract Residuals**: Calculate $\epsilon_t = Y_t - \text{Trend}_t - S_t$. These residuals represent the stochastic "noise" or natural variability of the system, independent of the deterministic trend.12
3. **Reconstruct Current State**: Add these residuals to the current trend value (at time $T_{now}$): $Y'_{t} = \text{Trend}_{now} + \epsilon_t$.
4. **Calculate Percentile**: Apply the Wilson-Hazen method to this reconstructed dataset $Y'$.

**Benefit**: This provides a percentile that represents the current magnitude of the variable, assuming the variability (variance) has remained constant while the mean has shifted.36

### 5.3 Method 2: Quantile Regression

A more rigorous and increasingly standard approach is Quantile Regression.11 Unlike OLS regression which models the conditional mean, quantile regression models the conditional percentile (e.g., 95th) directly as a function of time.

* **Model**: $Q_{0.95}(Y_t | t) = \beta_0 + \beta_1 t$.
* **Application**: This allows the 95th percentile to vary over time. The "current attribute state" is simply the predicted value of this regression line at the end of the monitoring period.
* **Uncertainty**: Confidence intervals for the quantile regression estimate can be generated (often via bootstrapping the regression coefficients).12
* **Superiority**: This method does not assume constant variance (homoscedasticity). If the river is becoming both cleaner (lower mean) and more stable (lower variance), quantile regression will capture the tightening of the 95th percentile correctly, whereas simple detrending might not.

## 6. Integrated Recommendations and Workflow

To satisfy the dual requirements of the NPS-FM (accounting for natural variability/sampling error) and the statistical reality of the data (autocorrelation/trend), the following integrated workflow is recommended.

### 6.1 Step 1: Diagnostic Screening

Before applying the Wilson-Hazen method, run diagnostics on the time series:

1. **Test for Trend**: Use the Mann-Kendall test (for monotonic trend) or Seasonal Kendall test (if seasonality is present).
   * **Result**: If $p < 0.05$, the stationarity assumption is violated. Proceed to Trend Modifications (Section 6.3).
2. **Test for Autocorrelation**: Calculate the Autocorrelation Function (ACF). Check if the lag-1 correlation ($\rho_1$) is significantly different from zero (typically if it exceeds $2/\sqrt{n}$).
   * **Result**: If significant, the independence assumption is violated. Proceed to Autocorrelation Modifications (Section 6.2).

### 6.2 Step 2: Handling Autocorrelation (If no trend)

If the data is stable (no trend) but dependent (autocorrelated):

1. **Calculate $n_{eff}$**: Use the lag-1 formula $n_{eff} = n \frac{1-\rho_1}{1+\rho_1}$.
   * **Refinement**: If the sample size is small ($n < 30$), use the Korn-Graubard adjustment logic to be conservative, effectively treating the time-series blocks as clusters.
2. **Adjust Wilson Formula**: Input $n_{eff}$ into the Wilson Score Interval formula instead of $n$.
   * **Formula**:
   $$CI = \frac{\hat{p} + \frac{z^2}{2n_{eff}} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n_{eff}} + \frac{z^2}{4n_{eff}^2}}}{1 + \frac{z^2}{n_{eff}}}$$
   * **Note**: The point estimate (Hazen rank) should generally still use $n$ (or the weighted equivalent) to remain unbiased, but the interval width must be driven by $n_{eff}$.

### 6.3 Step 3: Handling Trends

If a trend is detected:

* **Preferred Method**: Use Quantile Regression against time to estimate the 95th percentile at the end of the compliance period.
* **Alternative Method (if data is sparse)**: Detrend the data to the current year (as per Section 5.2), then apply the Autocorrelation-Adjusted Wilson-Hazen method to the detrended dataset.

### 6.4 Communicating Results

The NIWA report 1 emphasizes that "natural variability" encompasses real environmental cycles. When reporting these adjusted intervals:

* **Transparency**: Explicitly state that the confidence interval has been "adjusted for serial correlation ($n_{eff} = X$)."
* **Interpretation**: A wider interval due to $n_{eff}$ adjustment is not a failure of data collection; it is an honest representation of the ecosystem's persistence. It prevents the regulatory error of declaring a site "compliant" when the limited effective data does not support that conclusion.

## 7. Conclusion

The "Wilson-Hazen" method is a sound statistical baseline for environmental percentile estimation, offering significant theoretical advantages over normality-based methods for skewed, bounded water quality data. However, its standard application assumes independent data, a condition rarely met in environmental monitoring.

Research conclusively shows that autocorrelation creates a "false precision" by inflating the apparent sample size. To meet the regulatory requirement of "accounting for sampling error" under the NPS-FM, it is strictly necessary to modify the method.

* **For Autocorrelation**: The integration of Effective Sample Size ($n_{eff}$) into the Wilson Score formula is the most direct and defensible modification. It widens the confidence intervals to accurately reflect the redundancy in time-series data.
* **For Trends**: The use of static percentiles on trending data is methodologically unsound. Quantile Regression or Detrending must be employed to estimate the current state rather than a historical average.

By adopting these specific modifications—diagnosing the series first, then adjusting $n$ to $n_{eff}$ or modeling the trend—councils can transform the Wilson-Hazen method from a static textbook tool into a robust, defensible framework for dynamic environmental compliance.

### Table 1: Comparative Summary of Statistical Approaches

| Method | Best For | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Standard Wilson-Hazen** | Independent, stationary data. | Robust to skew; respects 0/1 bounds; simple calculation. | Underestimates error for autocorrelated data; invalid for trending data. |
| **$n_{eff}$-Adjusted Wilson** | Autocorrelated, stationary data. | Corrects for "false precision" of serial correlation; retains Wilson benefits. | Requires estimation of $\rho$ (autocorrelation); $n_{eff}$ formula varies by process type. |
| **Block Bootstrap** | Complex correlation structures. | Non-parametric; requires no assumptions about correlation shape. | Computationally intensive; requires careful choice of block size. |
| **Quantile Regression** | Trending (non-stationary) data. | Estimates current state dynamically; handles changing variance. | Requires larger sample sizes for stability; more complex to explain to stakeholders. |
