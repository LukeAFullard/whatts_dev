# whatts

**Wilson-Hazen statistics for Autocorrelated Trending Time Series**

`whatts` is a Python library designed to calculate rigorous regulatory compliance statistics (specifically the 95th percentile) for environmental time series. It moves beyond simple summary statistics by accounting for the two most common features of environmental data: **Trends** (non-stationarity) and **Autocorrelation** (serial dependence).

## Features

*   **Current State Projection:** Projects historical data to the present day using Sen's Slope, preventing historical "smearing" of improving or degrading trends.
*   **Effective Sample Size ($n_{eff}$):** Adjusts confidence intervals using the Bayley & Hammersley method to account for redundant information in autocorrelated data.
*   **One-Sided Tolerance Limits:** Calculates the **Upper Tolerance Limit (UTL)** (95% Confidence of the 95th Percentile), providing a legally defensible "ceiling" for compliance.
*   **Probability of Compliance:** Estimates the statistical confidence (0–100%) that a site meets a regulatory limit.
*   **Explainer Plots:** Generates visualizations to explain the "Projection" method to stakeholders.
*   **Sensitivity Analysis:** Comparison tables to show the impact of detrending and autocorrelation adjustments.

## Installation

```bash
pip install whatts
```

## Usage

### Basic Compliance Check

```python
import pandas as pd
from whatts import calculate_tolerance_limit

# Load your data
df = pd.read_csv("river_data.csv") # Requires 'Date' and 'Value' columns

# Calculate Compliance
result = calculate_tolerance_limit(
    df,
    date_col="Date",
    value_col="Value",
    target_percentile=0.95,
    confidence=0.95,
    regulatory_limit=540  # Optional: Limit to check against
)

# Output
print(f"Point Estimate (95th %ile): {result['point_estimate']:.2f}")
print(f"Upper Tolerance Limit (95% Conf): {result['upper_tolerance_limit']:.2f}")

if result['probability_of_compliance']:
    print(f"Confidence of Compliance: {result['probability_of_compliance']:.1%}")
```

### Visualizing the Method

```python
from whatts import plot_compliance_explainer

# ... (after running calculation) ...
fig = plot_compliance_explainer(
    dates=df['Date'],
    values=df['Value'],
    projected_values=result['projected_data'],
    result_dict=result
)
fig.show()
```

### Comparing Methods (Sensitivity Analysis)

```python
from whatts import compare_compliance_methods

table = compare_compliance_methods(df, "Date", "Value", regulatory_limit=540)
print(table)
```

## Communication & Interpretation Guide

In environmental regulation, interpreting statistical confidence is critical.

### The "Golden Rule" of Interpretation

**Never say:** *"There is an 87% chance the site is compliant."* (This implies the water varies, which it does, but that's not what the stat measures).

**Always say:** *"We are **87% confident** that the true 95th percentile is below the regulatory limit."* (This emphasizes that the uncertainty lies in our *knowledge* of the system).

### The "Traffic Light" System

| Probability Score | Interpretation | Regulatory Status | Recommended Wording |
| --- | --- | --- | --- |
| **> 95%** | **High Confidence Compliance** | **PASS** | "The site meets the target. We have high statistical confidence (>95%) that the current 95th percentile is below the limit." |
| **50% – 95%** | **Indeterminate (Likely Compliant)** | **ALERT / CHECK** | "The best estimate suggests the site meets the target, but due to sampling uncertainty (N_eff), we cannot confirm this with 95% confidence." |
| **5% – 50%** | **Indeterminate (Likely Failing)** | **ALERT / FAIL** | "The best estimate suggests the site exceeds the target. While statistical confidence is low (<95%), the risk of non-compliance is elevated." |
| **< 5%** | **High Confidence Failure** | **FAIL** | "The site fails to meet the target. We have high statistical confidence (>95%) that the current 95th percentile exceeds the limit." |

### Boilerplate Text for Reports

> **Assessment Methodology:**
> Compliance was assessed using the `whatts` framework. This method projects historical data to the current date to account for observed trends (Sen’s Slope) and adjusts confidence intervals to account for the redundancy inherent in serial monitoring data (Effective Sample Size, $n_{eff}$).
>
> **Statistical Interpretation:**
> The "Confidence of Compliance" reported represents the statistical probability that the true 95th percentile of the current state distribution is less than or equal to the regulatory limit. A value of 95% or higher is required to meet the definition of "High Confidence Compliance".
