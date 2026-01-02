# Practical Workflow for Compliance Assessment: Balancing Rigor and Utility

This is a classic conflict between **statistical rigor** (which demands acknowledging complexity) and **regulatory utility** (which demands a simple binary "Pass/Fail").

You are absolutely right to be wary of Quantile Regression (QR) in this context. While the report identifies it as "superior" theoretically, practical implementation with $n=30$ to $n=60$ is dangerous. QR requires a lot of data to estimate tails (like the 95th percentile) stably. With only 30 data points, the confidence intervals on a QR slope at the 95th percentile will be massive and likely unstable.

Here is a practical workflow that bridges the gap. It allows you to produce a **single number and Confidence Interval (CI)** that represents the "Current State," satisfying the regulator's need for simplicity while respecting the statistical reality of trends.

## The Solution: "Detrending and Projection" (The Section 5.2 Approach)

The report briefly mentions **Method 2: Detrending and Residual Analysis**. This is your "Goldilocks" solution. It removes the trend to stabilize the dataset, effectively "normalizing" the history to the present day, allowing you to treat the data as a single distribution again.

Here is the step-by-step logic you can apply:

### Step 1: Isolate the Trend (Theil-Sen)

Do not use standard OLS regression (it is too sensitive to outliers common in water data). Use the **Theil-Sen estimator** (often available in environmental stats packages). It draws a trend line based on the median of all slopes between data pairs.

* **Result:** You get a slope (e.g., "Nitrate is decreasing by 0.1 units/year").

### Step 2: Extract "Stationary" Residuals

Subtract the trend line from your actual data points.

* $Residual_t = Data_t - (Slope \times Time_t)$
* These residuals represent the *natural variability* (noise) of the site, stripped of the time-based improvement or degradation.

### Step 3: Project to "Current State"

This is the critical step for compliance. You take those residuals and add them to the **current** value of the trend line (Time = Now).

* $Projected_t = Residual_t + (Slope \times Time_{now})$
* **What this does:** It takes the variability you saw 4 years ago and asks, "If that same weather event happened today, with the current improved management, what would the result be?"

### Step 4: Apply Adjusted Wilson-Hazen

Now you have a "synthetic" dataset of 30–60 points that are all centered around the current date. You can now treat this as a single population.

1. **Calculate $n_{eff}$:** Run an autocorrelation check on the *residuals* (not the raw data). If significant autocorrelation exists, calculate the Effective Sample Size ($n_{eff}$) as per Section 4.2.1 of your report.
2. **Run Wilson-Hazen:** Calculate the 95th percentile and Wilson Score Interval using the projected dataset, but substitute $n$ with $n_{eff}$ in the interval formula.

## Why this solves your problem:

1. **It gives you ONE number:** You report the 95th percentile of the "Projected Current State."
2. **It gives you ONE Confidence Interval:** You can compare the Upper Confidence Limit (UCL) directly to the regulatory limit.
3. **It respects the Trend:** It doesn't penalize a site for bad data from 5 years ago if the site has genuinely improved.
4. **It works with $n=30$:** Unlike Quantile Regression, which tries to slice the data thin, this method uses *all* 30 residuals to estimate the distribution shape, maintaining your statistical power.

## A Warning on Sample Size ($n_{eff}$)

You mentioned you have 30 to 60 samples.

* **If $n_{eff} \ll n$:** If your data is autocorrelated (e.g., $\rho=0.6$), your $n_{eff}$ will drop to approximately **10**.
* **The Consequence:** A Wilson interval calculated with $n=10$ is going to be very wide. You might find that your compliance status is "Undetermined" (i.e., the target is inside the confidence interval).
* **The Defense:** This is not a failure of the method; it is the mathematical reality of the environment. If you only have 30 samples and they are correlated, you *do not* have enough information to be certain. Reporting a wide CI is the honest approach.

## Summary Recommendation for the Regulator/Client

When you present this, you can frame it as:

> "We assessed compliance using a **'Current State Projection'**.
> 1. We identified that water quality is improving/degrading over the assessment period.
> 2. We adjusted the historical data to reflect current conditions (removing the trend bias).
> 3. We calculated the 95th percentile on this current state, adjusting the confidence intervals for serial correlation to ensure we don't claim false certainty."
