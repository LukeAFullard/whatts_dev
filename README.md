# whatts

**Wilson-Hazen statistics for Autocorrelated Trending Time Series**

`whatts` is a Python library designed to calculate rigorous regulatory compliance statistics for environmental time series. It moves beyond simple summary statistics by accounting for the two most common features of environmental data that traditional methods ignore: **Trends** (non-stationarity) and **Autocorrelation** (serial dependence).

By projecting historical data to the current date and adjusting for effective sample size, `whatts` provides a legally defensible estimate of the **Upper Tolerance Limit (UTL)** (e.g., "We are 95% confident that the 95th percentile is below the limit").

## 🚀 Quick Start

Get started in seconds with this self-contained example:

```python
import pandas as pd
import numpy as np
from whatts import calculate_tolerance_limit, plot_compliance_explainer

# 1. Create dummy environmental data (improving trend + seasonality + noise)
dates = pd.date_range(start="2020-01-01", periods=50, freq="ME")
np.random.seed(42)
values = 100 - 0.5 * np.arange(50) + np.random.normal(0, 5, 50)
df = pd.DataFrame({"Date": dates, "Value": values})

# 2. Calculate Compliance Statistics
results = calculate_tolerance_limit(
    df,
    date_col="Date",
    value_col="Value",
    target_percentile=0.95, # We want the 95th percentile
    confidence=0.95,        # We want 95% confidence
    regulatory_limit=90     # The limit we must stay below
)

# 3. Print Results
print("--- Compliance Report ---")
print(f"Projected 95th Percentile: {results['point_estimate']:.2f}")
print(f"Upper Tolerance Limit (UTL): {results['upper_tolerance_limit']:.2f}")
print(f"Probability of Compliance:   {results['probability_of_compliance']:.1%}")

# 4. Visualize (requires matplotlib)
# fig = plot_compliance_explainer(df["Date"], df["Value"], results['projected_data'], results)
# fig.show()
```

## 📦 Installation

```bash
pip install whatts
```

*Dependencies: `numpy`, `pandas`, `scipy`, `mannks`, `matplotlib`*

## ✨ Key Features

*   **Current State Projection:** Projects historical data to the present day using **Sen's Slope**, preventing historical "smearing" where old, high values unfairly penalize an improving site.
*   **Effective Sample Size ($n_{eff}$):** Adjusts confidence intervals using the **Bayley & Hammersley** method to account for redundant information in autocorrelated data (e.g., weekly samples that aren't truly independent).
*   **One-Sided Tolerance Limits:** Calculates the **Upper Tolerance Limit (UTL)**, providing a defensible "ceiling" for compliance assessments.
*   **Probability of Compliance:** Estimates the statistical confidence (0–100%) that a site meets a regulatory limit using the **Score Test**.
*   **Defensible:** Built on standard environmental statistics methods (Wilson Score Interval, Hazen Plotting Position). Validated in `AUDIT_REPORT.md`.

## 📖 Usage Guide

### 1. Basic Compliance Check

The core function is `calculate_tolerance_limit`.

```python
from whatts import calculate_tolerance_limit

result = calculate_tolerance_limit(
    df,
    date_col="Date",
    value_col="Value",
    target_percentile=0.95, # The percentile you need to control (default 0.95)
    confidence=0.95,        # The statistical confidence level (default 0.95)
    regulatory_limit=540    # Optional: The numeric limit to check against
)
```

**Key Output Fields:**

| Key | Description |
| :--- | :--- |
| `point_estimate` | The "Face Value" 95th percentile of the projected data. |
| `upper_tolerance_limit` | The **Regulatory Assurance Value**. The top end of the confidence interval. |
| `probability_of_compliance` | The likelihood that the true percentile is below the regulatory limit (only if `regulatory_limit` is provided). |
| `trend_slope_per_year` | The detected trend slope in units per year (e.g., mg/L/year). |
| `n_eff` | The effective sample size used for calculations. |

### 2. Visualization

Explain the "Projection" method to stakeholders using the built-in explainer plot.

```python
from whatts import plot_compliance_explainer

fig = plot_compliance_explainer(
    dates=df['Date'],
    values=df['Value'],
    projected_values=result['projected_data'],
    result_dict=result
)
fig.show()
```

### 3. Sensitivity Analysis (Comparing Methods)

See how much the trend projection and autocorrelation adjustment affect your results.

```python
from whatts import compare_compliance_methods

table = compare_compliance_methods(df, "Date", "Value", regulatory_limit=540)
print(table)
```
*This returns a DataFrame comparing "Naive" (raw data), "Detrended Only", and "Full whatts" methods.*

## 🚦 Communication & Interpretation

In environmental regulation, interpreting statistical confidence is critical. We recommend the "Traffic Light" system.

### The "Golden Rule"
**Never say:** *"There is an 87% chance the site is compliant."* (This implies the water quality varies randomly, but the statistic is about our knowledge).
**Always say:** *"We are **87% confident** that the true target percentile is below the regulatory limit."*

### The Traffic Light System

| Probability Score | Interpretation | Regulatory Status | Recommended Wording |
| :--- | :--- | :--- | :--- |
| **> 95%** | **High Confidence Compliance** | **PASS** | "We have high statistical confidence (>95%) that the site meets the target." |
| **50% – 95%** | **Indeterminate (Likely Compliant)** | **CHECK** | "The best estimate suggests the site passes, but due to sampling uncertainty, we cannot confirm this with 95% confidence." |
| **5% – 50%** | **Indeterminate (Likely Failing)** | **ALERT** | "The best estimate suggests the site fails. While confidence is low (<95%), the risk of non-compliance is elevated." |
| **< 5%** | **High Confidence Failure** | **FAIL** | "We have high statistical confidence (>95%) that the site fails to meet the target." |

## 🔍 Methodology & Audit

This library has undergone a comprehensive code and methodology audit.
See **`AUDIT_REPORT.md`** for full details on:
*   Validation of the **Wilson-Hazen** method.
*   Correctness of the **Mann-Kendall** trend test and **Sen's Slope** projection.
*   Implementation of the **Chi-Square Boundary Correction** for small sample sizes.
