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

### Span Tree Model

The adaptive hierarchy constructs a **trace tree** $T = (V, E)$ where:

$$
V = \{\sigma_1, \sigma_2, \ldots, \sigma_n\} \quad \text{(spans)}
$$

$$
E = \{(\sigma_i, \sigma_j) \mid \sigma_j \text{ is child of } \sigma_i\}
$$

The tree invariant ensures exactly one root per trace:

$$
|\{\sigma \in V \mid \text{parent}(\sigma) = \emptyset\}| = 1
$$

When a child span is created, the parent span's attributes are enriched with metadata, creating a **bidirectional information flow**:

$$
\text{create\_child}(\sigma_{parent}, n, \mathbf{I}, \mathbf{O}, \mathbf{M}) \implies
\begin{cases}
\text{attrs}(\sigma_{parent}) \leftarrow \text{attrs}(\sigma_{parent}) \cup \mathbf{M} \\
\text{attrs}(\sigma_{child}) \leftarrow \mathbf{I} \cup \mathbf{O} \cup \mathbf{M}
\end{cases}
$$

### Context Propagation Semantics

The `with mlflow.start_span(name=name) as span` construct uses Python's context manager protocol (`__enter__`/`__exit__`), which guarantees:

$$
\text{span.start\_time} \leq \text{span.end\_time} \quad \text{(temporal ordering)}
$$

$$
\forall \sigma_{child} \in \text{children}(\sigma_{parent}): \quad [\sigma_{child}.start, \sigma_{child}.end] \subseteq [\sigma_{parent}.start, \sigma_{parent}.end]
$$

This nesting property enables **waterfall visualization** of LLM traces in the MLflow Tracing UI.

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
- **Context lookup:** $O(1)$ — thread-local storage access

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

### GenAI Metric Formalization

#### Answer Similarity ($\phi_{sim}$)

Uses an LLM-as-a-Judge to evaluate semantic similarity between model output and ground truth:

$$
\phi_{sim}(r_i, g_i) = \text{LLM\_Judge}(\text{prompt}_{sim}, r_i, g_i) \in [1, 5]
$$

Where $r_i$ is the model's response and $g_i$ is the ground truth. The judge evaluates on a 1-5 Likert scale based on semantic overlap, paraphrase detection, and information coverage.

#### Answer Relevance ($\phi_{rel}$)

Evaluates whether the response is relevant to the original question:

$$
\phi_{rel}(r_i, q_i) = \text{LLM\_Judge}(\text{prompt}_{rel}, r_i, q_i) \in [1, 5]
$$

This metric captures hallucination (irrelevant content) and topic drift in LLM responses.

#### Toxicity ($\phi_{tox}$)

Uses a classifier to detect toxic content in generated text:

$$
\phi_{tox}(r_i) = P(\text{toxic} \mid r_i) \in [0, 1]
$$

Typically implemented via a fine-tuned classifier (e.g., RoBERTa-based) rather than LLM-as-Judge.

### Aggregate Model Ranking

The comparison matrix enables model ranking via weighted aggregation:

$$
\text{score}(m_j) = w_{sim} \cdot \bar{\phi}_{sim}(m_j) + w_{rel} \cdot \bar{\phi}_{rel}(m_j) - w_{tox} \cdot \bar{\phi}_{tox}(m_j)
$$

Where $\bar{\phi}_x(m_j) = \frac{1}{N}\sum_{i=1}^{N} \phi_x(r_i^{(j)}, g_i)$ is the mean metric across all samples.

Note: Toxicity is subtracted because lower is better.

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
- **LLM calls:** $O(k \cdot N \cdot 2)$ — similarity and relevance each require one LLM judge call per sample

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

### Type Dispatch Analysis

The type dispatch is an instance of the **Visitor Pattern** applied to data types:

| Input Type | Action | MLflow Converter | Status |
|:---|:---|:---|:---|
| `pd.DataFrame` | Log as MLflow dataset | `mlflow.data.from_pandas()` | ✅ Implemented |
| `np.ndarray` | Should log as numpy | `mlflow.data.from_numpy()` | ❌ Not implemented |
| `dict` | Should convert first | `pd.DataFrame.from_dict()` → `from_pandas()` | ❌ Not implemented |
| Other | Warning printed | N/A | ⚠️ Silent degradation |

### Exception Safety

The entire method is wrapped in a `try/except Exception` block:

$$
\text{safe\_log}(d, c) =
\begin{cases}
\text{log\_dataset}(d, c) & \text{if no exception} \\
\text{print}(\text{error}) & \text{otherwise (silent failure)}
\end{cases}
$$

This prevents dataset logging failures from interrupting the main experiment pipeline — a defensive decision that trades observability for reliability.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $d$ | `dataset_source` | `Any` | `mlflow_tracker.py:L20` |
| $c$ | `context` | `str` | `mlflow_tracker.py:L20` |

### Complexity Analysis

- **Time:** $O(N)$ — where $N$ is the number of rows in the DataFrame (conversion cost)
- **Space:** $O(N)$ — MLflow creates an in-memory copy of the dataset

---

## Algorithm 4: Context Manager Span Lifecycle

**Source:** [mlflow_tracker.py:L81-L89](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L81-L89)

### Description

The `start_span` method uses Python's `@contextlib.contextmanager` decorator to create a **generator-based context manager** that wraps MLflow span creation. It provides deterministic span lifecycle management with automatic cleanup, regardless of whether the enclosed code succeeds or fails.

### Formal Representation

The context manager implements the Resource Acquisition Is Initialization (RAII) pattern:

$$
\text{start\_span}(n, \mathbf{I}) = \text{with}(\text{mlflow.start\_span}(n)) \text{ as } \sigma
$$

$$
\begin{cases}
\sigma.\text{set\_inputs}(\mathbf{I}) & \text{if } \mathbf{I} \neq \text{None} \\
\text{yield } \sigma & \text{(control returns to caller)} \\
\sigma.\text{end}() & \text{(automatic on context exit)}
\end{cases}
$$

### Span Lifecycle Guarantees

The `with` statement provides two critical guarantees:

1. **Resource cleanup:** Span is closed even if an exception occurs:

$$
\forall \sigma: \quad \text{with}(\sigma) \implies \text{finally: } \sigma.\text{\_\_exit\_\_}()
$$

2. **Temporal containment:** All work performed within the `with` block is strictly contained within the span's time window:

$$
t_{enter} \leq t_{work} \leq t_{exit} \implies [t_{enter}, t_{exit}] \supseteq [t_{work\_start}, t_{work\_end}]
$$

### Generator vs. Class-Based Context Manager

The `@contextmanager` decorator converts a generator function into a context manager:

```python
@contextmanager
def start_span(name, inputs):
    with mlflow.start_span(name) as span:  # __enter__
        if inputs:
            span.set_inputs(inputs)
        yield span                           # control to caller
    # __exit__ (automatic span close)
```

This is more concise than the equivalent class-based approach (which requires `__enter__` and `__exit__` methods), while providing identical semantics.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $n$ | `name` | `str` | `mlflow_tracker.py:L82` |
| $\mathbf{I}$ | `inputs` | `Optional[Dict]` | `mlflow_tracker.py:L82` |
| $\sigma$ | `span` | `Span` | `mlflow_tracker.py:L86` |

### Complexity Analysis

- **Time:** $O(1)$ — span creation + optional input setting
- **Space:** $O(|\mathbf{I}|)$ — input dictionary stored on span

---

## Algorithm 5: Experiment Initialization with URI Configuration

**Source:** [mlflow_tracker.py:L11-L14](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L11-L14)

### Description

The `MLflowTracker` constructor performs a two-step initialization: (1) sets the MLflow tracking server URI, and (2) creates or selects the experiment by name. This establishes a global MLflow context that all subsequent logging calls operate within.

### Formal Representation

Let $U$ be the tracking URI and $E$ be the experiment name:

$$
\text{init}(U, E) = \text{set\_experiment}(\text{set\_uri}(U), E)
$$

The initialization establishes a global singleton state:

$$
\text{mlflow.\_tracking\_uri} \leftarrow U
$$

$$
\text{mlflow.\_active\_experiment} \leftarrow
\begin{cases}
\text{get\_experiment}(E) & \text{if } E \text{ exists on server} \\
\text{create\_experiment}(E) & \text{otherwise}
\end{cases}
$$

### Global State Implications

MLflow uses module-level global state, meaning:

$$
\forall \text{MLflowTracker instances } t_1, t_2: \quad t_2.\text{init}(U_2, E_2) \implies t_1.\text{context} = (U_2, E_2)
$$

The last-writer-wins semantic means multiple `MLflowTracker` instances will **overwrite** each other's configurations. This is a known MLflow limitation, not a Yantra design flaw.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $U$ | `tracking_uri` | `str` | `mlflow_tracker.py:L12` |
| $E$ | `experiment_name` | `str` | `mlflow_tracker.py:L12` |

### Complexity Analysis

- **Time:** $O(1)$ locally; $O(N_{net})$ for remote tracking server
- **Space:** $O(1)$ — URI and experiment name stored as module globals

---

## Algorithm 6: Framework-Specific Autologging

**Source:** [mlflow_tracker.py:L36-L40](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/observability/mlflow_tracker.py#L36-L40)

### Description

The `autolog_crewai()` and `autolog_gemini()` methods activate MLflow's automatic logging for specific AI frameworks. These instrumentations intercept framework API calls and automatically log traces, metrics, and parameters without requiring explicit logging calls in user code.

### Formal Representation

The autologging can be modeled as an aspect-oriented programming (AOP) interceptor:

$$
\text{autolog}(F) = \text{monkey\_patch}(F.\text{API}, \text{MLflow.trace})
$$

Where $F$ is the target framework (CrewAI or Gemini) and the monkey-patching wraps each API call:

$$
F.\text{call}(args) \xrightarrow{\text{autolog}} \text{MLflow.start\_span}() \to F.\text{call}(args) \to \text{MLflow.end\_span}()
$$

### Framework Instrumentation Matrix

| Framework | Autolog Method | What Gets Logged | MLflow Version |
|:---|:---|:---|:---|
| CrewAI | `mlflow.crewai.autolog()` | Agent tasks, crew execution, tool calls | ≥2.14 |
| Gemini | `mlflow.gemini.autolog(log_traces=True)` | API calls, token counts, response content | ≥2.14 |

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $F_{crewai}$ | `mlflow.crewai` | module | `mlflow_tracker.py:L37` |
| $F_{gemini}$ | `mlflow.gemini` | module | `mlflow_tracker.py:L40` |

### Complexity Analysis

- **Time:** $O(1)$ — one-time monkey-patching setup
- **Space:** $O(1)$ — no additional data structures

---

## Cross-Algorithm Dependency Graph

The 6 algorithms span two lifecycle phases:

$$
\text{Setup Phase:} \quad A_5 \to A_6 \quad \text{(init → autolog)}
$$

$$
\text{Runtime Phase:} \quad A_4 \to A_1 \to A_3 \quad \text{(span → trace → dataset)}
$$

$$
\text{Evaluation Phase:} \quad A_2 \quad \text{(arena — standalone)}
$$

| Algorithm | Phase | Depends On | Called By |
|:---|:---|:---|:---|
| A1 (Adaptive Span) | Runtime | A5 (URI context) | Client code via `log_llm_trace()` |
| A2 (Arena Evaluation) | Evaluation | A5 (URI context) | Client code via `compare_models()` |
| A3 (Dataset Logging) | Runtime | A5 (URI context) | Client code via `log_dataset()` |
| A4 (Context Manager Span) | Runtime | A5 (URI context) | Client code via `start_span()` |
| A5 (Initialization) | Setup | None | Constructor |
| A6 (Autologging) | Setup | A5 (URI context) | Client code (optional) |
