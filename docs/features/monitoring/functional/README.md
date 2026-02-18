# Monitoring Module - Functional Documentation

## Overview
The **Monitoring** module ensures the ongoing quality and reliability of your LLM applications by analyzing production logs. It specifically focuses on **text quality metrics** (e.g., sentiment, toxicity, length) to detect drift or degradation in model performance over time.

## Capabilities

### 1. Automated Quality Reports
-   **HTML Reports:** Generates visual, interactive HTML reports summarizing the quality of model responses.
-   **Text Analysis:** Automatically computes metrics such as:
    -   Response length
    -   Sentiment analysis
    -   Out-of-Vocabulary (OOV) words
    -   Text complexity
-   **Drift Detection:** (Implicit via Evidently) Can compare current production data against a reference baseline to identify data drift.

### 2. Plug-and-Play Architecture
-   **Protocol-Based:** The system is designed to be backend-agnostic. While **Evidently AI** is the default provider, you can swap it for other monitoring tools (DeepChecks, Whylogs) without changing your application code.

## Usage

### Generating a Report
To generate a quality report from a pandas DataFrame containing logs:

```python
from yantra.domain.monitoring.quality import EvidentlyQualityMonitor
import pandas as pd

# 1. Load your logs
df_logs = pd.DataFrame({
    "response": [
        "This product is amazing!",
        "I hate this service.",
        "The weather is neutral."
    ]
})

# 2. Initialize Monitor
monitor = EvidentlyQualityMonitor()

# 3. Generate Report
report_path = monitor.generate_report(
    df_logs=df_logs,
    output_path="reports/daily_quality.html",
    text_column="response"
)

print(f"Report generated at: {report_path}")
```
