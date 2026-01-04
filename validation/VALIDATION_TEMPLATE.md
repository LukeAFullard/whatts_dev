# Validation: [Test Case Name]

## 1. Test Description
**What is being tested:**
[Brief description of the specific scenario, feature, or edge case being validated. E.g., "Detection of a +2σ immediate step change with strong seasonality."]

**Category:**
[E.g., Effect Morphology, Statistical Challenge, Data Quality, etc.]

## 2. Rationale
**Why this test is important:**
[Explanation of why this validation is necessary. E.g., "To ensure the detector can distinguish a moderate signal from strong background seasonality, mimicking common environmental intervention scenarios."]

## 3. Success Criteria
**Expected Outcome for Pass:**
[Specific, measurable criteria that must be met to consider the test a pass.]
- [ ] **Detection:** [E.g., P-value < 0.05, Effect detected]
- [ ] **Accuracy:** [E.g., Estimated effect size within 10% of true value]
- [ ] **False Positives:** [E.g., No detection in placebo period]
- [ ] **Diagnostics:** [E.g., No warnings triggered, or specific warning triggered]
- [ ] **Robustness:** [E.g., Result robust across >80% of sensitivity specifications]

## 4. Data Generation
**Data Characteristics:**
- **History Length:** [E.g., 10 years]
- **Seasonality:** [E.g., Sine wave amplitude 5.0]
- **Noise:** [E.g., White noise sigma 1.0]
- **Treatment:** [E.g., Additive step +2.0 starting at T=0]
- **Gaps/Issues:** [E.g., None, or specific missing data pattern]

## 5. Validation Code
**Step-by-Step Implementation:**

```python
import pandas as pd
import numpy as np
# Import your package modules here
# from whatts import ...
import matplotlib.pyplot as plt

# 1. Setup Configuration
# [Explain choice of parameters]

# 2. Generate Synthetic Data
# [Code to generate the dataframe]
# df = ...

# 3. Plot Raw Data
# fig, ax = plot_raw_timeseries(...)
# fig.savefig("raw_data.png")

# 4. Initialize and Run Analysis
# [Code to run the test]

# 5. Print Results
# print(results)

# 6. Plot Results/Envelopes
# fig.savefig("results.png")

# 7. Plot Diagnostics
# fig.savefig("diagnostics.png")
```

## 6. Results Output
**Console/Text Output:**
```text
[Paste the actual text output, dictionary, or log from the code execution here]
```

## 7. Visual Evidence
**Raw Data:**
![Raw Data Plot](raw_data.png)
*[Caption describing the input data.]*

**Results Plot:**
![Results Plot](results.png)
*[Caption describing what is seen in the plot.]*

**Diagnostics:**
![Diagnostics Plot](diagnostics.png)
*[Caption describing the diagnostic plots.]*

## 8. Interpretation & Conclusion
**Analysis:**
[Detailed interpretation of the results. Did the detector behave as expected? Were the estimates accurate? Did any unexpected warnings appear?]

**Diagnostics Interpretation:**
[Review of the diagnostic plots. Do they support the validity of the analysis? Are the assumptions of the model met?]

**Pass/Fail Status:**
- [ ] **PASS**
- [ ] **FAIL**

**Notes:**
[Any additional observations or follow-up actions required.]
