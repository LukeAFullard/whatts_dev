# Future Features Roadmap

This document outlines high-value suggestions to make the `whatts` package significantly more useful for **regulatory reporting** and **stakeholder buy-in**.

Since the methodology involves a shift from "Standard Wilson-Hazen" to "Projected Current State", tools are needed to answer the question: *"Why is this number different from what we used to get?"* visually and numerically.

### 1. Add an "Explainer Plot" Module

It is difficult to explain "Detrended Projection" with words alone. A visualization makes it obvious. We suggest adding a `plot_compliance()` function that produces a specific 2-panel figure:

* **Left Panel (Time Series):** Shows the raw data, the Sen's Slope trend line, and arrows indicating how past points are "pushed" up or down to the current date.
* **Right Panel (Distribution):** Shows the **Projected** data as a histogram or rug plot, with the calculated 95th percentile and the Confidence Interval band overlaid.

**Proposed Code snippet for `src/whatts/plotting.py`:**

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_compliance_explainer(dates, values, projected_values, result_dict):
    """
    Visualizes the 'Current State Projection'.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={'width_ratios': [3, 1]})

    # --- Panel 1: Time Series & Projection ---
    # Plot Raw Data
    ax1.scatter(dates, values, color='gray', alpha=0.5, label='Historical Data')

    # Plot Projected "Current State" (clustered at the final date)
    current_date = dates.max()
    ax1.scatter([current_date]*len(values), projected_values,
                color='blue', alpha=0.6, label='Projected Current State')

    # Draw arrows connecting History to Projection
    for d, v, p in zip(dates, values, projected_values):
        ax1.plot([d, current_date], [v, p], color='blue', alpha=0.1)

    ax1.set_title("Step 1: Projecting History to Current State")
    ax1.legend()

    # --- Panel 2: The Assessment ---
    # Histogram of Projected Data
    ax2.hist(projected_values, orientation='horizontal', color='blue', alpha=0.3, density=True)

    # The Statistic
    # Note: result_dict structure depends on implementation (e.g. 'upper_tolerance_limit')
    stat_val = result_dict['point_estimate']
    utl = result_dict['upper_tolerance_limit']

    ax2.axhline(stat_val, color='red', linewidth=2, label='95th %ile')
    ax2.axhline(utl, color='red', linestyle='--', label='UTL (95% Conf)')

    ax2.set_title("Step 2: Assessing Compliance")
    ax2.set_ylim(ax1.get_ylim()) # Match y-axis
    ax2.axes.get_xaxis().set_visible(False) # Hide x-axis density

    plt.tight_layout()
    return fig
```

### 2. Implement a "Comparison Table" Function

Regulators will want to see a sensitivity analysis. We suggest adding a utility that runs the assessment **three ways** and outputs a pandas DataFrame comparing them:

1. **Naive:** Raw data, Standard Wilson-Hazen (The "Old Way").
2. **Detrended Only:** Projected data, Standard Wilson-Hazen (Fixes trend, ignores $n_{eff}$).
3. **Full `whatts`:** Projected data + $n_{eff}$ correction (The "Correct Way").

This table acts as a "shield," showing exactly how much the trend affected the result, and how much the autocorrelation widened the confidence interval.

### 3. Hard-Code a "Minimum Record Length" Warning

If $n_{eff} \approx 10$, results can be unstable.

* If $n < 10$, `mannks` (Sen's Slope) becomes unstable.
* If $n_{eff} < 10$, Wilson calculations can sometimes result in absurdly small numbers if correlation is high.

**Suggestion:** Add a strict check in `core.py`:

```python
if n_eff < 10:
    warnings.warn(
        f"Effective Sample Size is extremely low ({n_eff:.1f}). "
        "Compliance results will have very wide confidence intervals "
        "and may be uninformative."
    )
```

This manages expectations before the user sees a confidence interval that spans from 0 to Infinity.

### 4. Communication & Interpretation Guide

In environmental law, words like "Probability" and "Risk" have specific legal meanings. If you say "There is an 87% probability of compliance," a layperson hears "87% of the time the water is clean." **This is incorrect.**

You are calculating the **confidence in a statistic**, not the frequency of clean water.

Here is your "Style Guide" for accurately communicating the outputs of `whatts`.

#### The "Golden Rule" of Interpretation

**Never say:** *"There is an 87% chance the site is compliant."*
(This sounds like a gamble or a weather forecast).

**Always say:** *"We are **87% confident** that the true 95th percentile is below the regulatory limit."*
(This emphasizes that the uncertainty lies in our *knowledge* of the system, not just the system itself).

#### The "Traffic Light" Classification System

To make this usable for managers without losing rigor, I recommend mapping the continuous probability score to discrete "Confidence Categories."

| Probability Score | Interpretation | Regulatory Status | Recommended Wording |
| --- | --- | --- | --- |
| **> 95%** | **High Confidence Compliance** | **PASS** | "The site meets the target. We have high statistical confidence (>95%) that the current 95th percentile is below the limit." |
| **50% – 95%** | **Indeterminate (Likely Compliant)** | **ALERT / CHECK** | "The best estimate suggests the site meets the target, but due to sampling uncertainty (N_eff), we cannot confirm this with 95% confidence. Continued monitoring is required." |
| **5% – 50%** | **Indeterminate (Likely Failing)** | **ALERT / FAIL** | "The best estimate suggests the site exceeds the target. While statistical confidence is low (<95%), the risk of non-compliance is elevated." |
| **< 5%** | **High Confidence Failure** | **FAIL** | "The site fails to meet the target. We have high statistical confidence (>95%) that the current 95th percentile exceeds the limit." |

#### "Do Not Say" – The Forbidden Phrases

| ❌ **Don't Say This** | ✅ **Say This Instead** | **Why?** |
| --- | --- | --- |
| "The site is safe 87% of the time." | "We are 87% confident the 95th percentile is safe." | The 95th percentile *already* allows for 5% exceedance. You are measuring the error bar on the percentile, not the water itself. |
| "The trend proves the water is better." | "Projection analysis indicates the water quality has likely improved..." | Trends are estimates, not proofs. "Indicates" or "suggests" is safer than "proves." |
| "The sample size was too small." | "The *Effective Sample Size ($n_{eff}$)* was reduced due to autocorrelation..." | "Too small" sounds like you made a mistake. "Reduced due to autocorrelation" places the blame on the *river's physics*, not the sampler. |

#### Boilerplate Text for your Reports

Here is a standard paragraph you can drop into your executive summary. It is legally defensive and statistically accurate:

> **Assessment Methodology:**
> Compliance was assessed using the `whatts` framework (Wilson-Hazen for Autocorrelated Trending Time Series). This method projects historical data to the current date to account for observed trends (Sen’s Slope) and adjusts confidence intervals to account for the redundancy inherent in serial monitoring data (Effective Sample Size, $n_{eff}$).
> **Statistical Interpretation:**
> The "Confidence of Compliance" reported below represents the statistical probability that the true 95th percentile of the current state distribution is less than or equal to the regulatory limit. A value of 95% or higher is required to meet the definition of "High Confidence Compliance" typically required for regulatory assurance.

#### A Visual Analogy for Clients

When a client asks, *"Why is my confidence only 80%? The point is below the line!"*, use the **"Blurry Photo"** analogy:

> "Imagine the regulatory limit is a finish line. We took a photo of your runner (the 95th percentile) crossing the line.
> Because of the trend and the correlation, the photo is **blurry** (wide confidence interval).
> In the blurry photo, your runner *looks* like they are ahead of the line (Point Estimate < Limit). But the blur overlaps the line. The '80%' means that based on this blurry photo, there is still a 20% chance that the runner's nose was actually behind the line. We need a clearer photo (more samples) or a faster runner (better improvement) to be sure."
