# Observability Module - Mathematical Logic

## Algorithm 1: Adaptive Span Hierarchy Construction

**Source:** [mlflow_tracker.py:L54-L79](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L54-L79)

### Description

The `log_llm_trace` method implements an adaptive span hierarchy algorithm. It inspects the current execution context and dynamically decides whether to create a **child span** (if a parent trace exists) or a **root span** (if no trace is active). This enables seamless nesting of LLM traces without explicit parent management.

### Formal Representation

Let $S$ be the set of all spans in the system, and let $\sigma_{active}$ denote the currently active span retrieved via `mlflow.get_current_active_span()`.

The span creation decision function $f_{span}$ is defined as:

$$
f_{span}(\sigma_{active}, \mathbf{I}, \mathbf{O}, \mathbf{M}) =
\begin{cases}
\text{create\_child}(\sigma_{active}, n, \mathbf{I}, \mathbf{O}, \mathbf{M}) & \text{if } \sigma_{active} \neq \emptyset \\
\text{create\_root}(n, \mathbf{I}, \mathbf{O}, \mathbf{M}) & \text{if } \sigma_{active} = \emptyset
\end{cases}
$$

Where:
- $n$ is the span name (`name: str`)
- $\mathbf{I} = \{(k_1, v_1), \ldots, (k_m, v_m)\}$ is the input dictionary (`inputs: Dict[str, Any]`)
- $\mathbf{O} = \{(k_1, v_1), \ldots, (k_p, v_p)\}$ is the output dictionary (`outputs: Dict[str, Any]`)
- $\mathbf{M} = \{(k_1, v_1), \ldots, (k_q, v_q)\}$ is the metadata dictionary (`metadata: Optional[Dict]`)

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\sigma_{active}$ | `root_span` | `Optional[Span]` | `mlflow_tracker.py:L61` |
| $n$ | `name` | `str` | `mlflow_tracker.py:L54` |
| $\mathbf{I}$ | `inputs` | `Dict[str, Any]` | `mlflow_tracker.py:L54` |
| $\mathbf{O}$ | `outputs` | `Dict[str, Any]` | `mlflow_tracker.py:L54` |
| $\mathbf{M}$ | `metadata` | `Optional[Dict]` | `mlflow_tracker.py:L55` |

### Complexity Analysis

- **Time:** $O(1)$ — single context check + span creation (no iteration)
- **Space:** $O(|\mathbf{M}|)$ — proportional to metadata size stored on the span

---

## Algorithm 2: Multi-Model Arena Evaluation

**Source:** [arena.py:L18-L70](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/arena.py#L18-L70)

### Description

The `ModelArena.compare_models` method implements a systematic model comparison pipeline. It iterates over $k$ model URIs, runs each against a shared evaluation dataset $D$, computes GenAI metrics (similarity, relevance, toxicity) via `mlflow.evaluate`, and aggregates results into a comparison DataFrame.

### Formal Representation

Given:
- Evaluation dataset $D = \{(q_i, g_i)\}_{i=1}^{N}$ where $q_i$ is a question and $g_i$ is ground truth
- Model set $\mathcal{M} = \{m_1, m_2, \ldots, m_k\}$ (provided as URIs)
- Metric functions $\phi = \{\phi_{sim}, \phi_{rel}, \phi_{tox}\}$

The evaluation produces:

$$
R_{j} = \text{mlflow.evaluate}(m_j, D, \phi) \quad \forall \, m_j \in \mathcal{M}
$$

The final comparison matrix $\mathbf{C}$ is:

$$
\mathbf{C} = \begin{bmatrix}
m_1 & \phi_{sim}(R_1) & \phi_{rel}(R_1) & \phi_{tox}(R_1) \\
m_2 & \phi_{sim}(R_2) & \phi_{rel}(R_2) & \phi_{tox}(R_2) \\
\vdots & \vdots & \vdots & \vdots \\
m_k & \phi_{sim}(R_k) & \phi_{rel}(R_k) & \phi_{tox}(R_k)
\end{bmatrix}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $D$ | `eval_data` | `pd.DataFrame` | `arena.py:L19` |
| $\mathcal{M}$ | `model_uris` | `List[str]` | `arena.py:L20` |
| $\phi_{sim}$ | `answer_similarity()` | `Metric` | `arena.py:L37` |
| $\phi_{rel}$ | `answer_relevance()` | `Metric` | `arena.py:L38` |
| $\phi_{tox}$ | `toxicity()` | `Metric` | `arena.py:L39` |
| $R_j$ | `evaluation` | `EvaluationResult` | `arena.py:L52` |
| $\mathbf{C}$ | return value | `pd.DataFrame` | `arena.py:L68-L70` |

### Complexity Analysis

- **Time:** $O(k \cdot N \cdot |\phi|)$ — $k$ models × $N$ samples × metric computation per sample
- **Space:** $O(k \cdot |\phi|)$ — stores metric results per model

---

## Algorithm 3: Type-Aware Dataset Logging

**Source:** [mlflow_tracker.py:L20-L34](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L20-L34)

### Description

The `log_dataset` method implements a type-dispatch pattern to convert arbitrary data sources into MLflow-compatible datasets. It performs runtime type checking and dispatches to the appropriate MLflow data converter.

### Formal Representation

$$
\text{log\_dataset}(d, c) =
\begin{cases}
\text{mlflow.log\_input}(\text{from\_pandas}(d), c) & \text{if } d \in \text{DataFrame} \\
\text{warn}(\text{type}(d)) & \text{otherwise}
\end{cases}
$$

Where $d$ is `dataset_source` and $c$ is the context string (`"input"`, `"output"`, etc.).

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $d$ | `dataset_source` | `Any` | `mlflow_tracker.py:L20` |
| $c$ | `context` | `str` | `mlflow_tracker.py:L20` |

### Complexity Analysis

- **Time:** $O(N)$ — where $N$ is the number of rows in the DataFrame (conversion cost)
- **Space:** $O(N)$ — MLflow creates an in-memory copy of the dataset
