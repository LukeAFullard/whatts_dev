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
