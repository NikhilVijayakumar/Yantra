# Observability Module - Functional Documentation

## Overview
The **Observability** module provides a unified interface for tracking experiments, logging metrics, and evaluating LLM performance. It abstracts the underlying tracking infrastructure (currently MLflow), allowing for seamless integration of experiment tracking into your AI workflows.

## Capabilities

### 1. Experiment Tracking
-   **Run Management:** Start and stop experiment runs, including nested runs.
-   **Metric Logging:** Log numerical metrics (accuracy, loss, latency) with step support.
-   **Parameter Logging:** Log configuration parameters (hyperparameters, model names).
-   **Artifact Logging:** Save and log files (models, plots, data) associated with runs.

### 2. LLM Tracing
-   **Trace Logging:** Capture detailed traces of LLM interactions, including inputs, outputs, and metadata.
-   **Span Management:** Create hierarchical spans to represent complex chains (e.g., RAG retrieval, generation).
-   **Vendor Integration:** Automatic logging support for CrewAI and Google Gemini.

### 3. System Monitoring
-   **Resource Metrics:** Automatically log CPU, RAM, and GPU usage during experiments.

### 4. Model Evaluation (The Arena)
-   **LLM Comparison:** Framework to compare different LLMs or prompts.
-   **LLM-as-a-Judge:** Uses MLflow Evaluate to compute GenAI metrics:
    -   **Answer Similarity:** How close the answer is to ground truth.
    -   **Answer Relevance:** How relevant the answer is to the question.
    -   **Toxicity:** Detects toxic content in outputs.

## Usage

### Basic Experiment Tracking
```python
from yantra.domain.observability import MLflowTracker

tracker = MLflowTracker(tracking_uri="http://localhost:5000", experiment_name="my_experiment")

with tracker.start_run(run_name="run_1"):
    tracker.log_param("model_type", "gpt-4")
    tracker.log_metric("accuracy", 0.95)
```

### LLM Tracing
```python
tracker.log_llm_trace(
    name="chat_completion",
    inputs={"prompt": "Hello"},
    outputs={"response": "Hi there!"},
    metadata={"tokens": 15}
)
```

### Comparing Models (Arena)
```python
from yantra.domain.observability.arena import ModelArena
import pandas as pd

arena = ModelArena(tracker_uri="http://localhost:5000")
eval_data = pd.DataFrame({
    "question": ["What is 2+2?"],
    "ground_truth": ["4"]
})

results = arena.compare_models(
    eval_data=eval_data,
    model_uris=["runs:/<run_id>/model"],
    run_name_prefix="math_test"
)
print(results)
```
