# Monitoring Module - Mathematical Logic

## Algorithm 1: Lazy NLTK Resource Acquisition

**Source:** [quality.py:L39-L55](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L39-L55)

### Description

The `EvidentlyQualityMonitor` implements a **lazy initialization** pattern for NLTK resources. On construction, it iterates over a fixed set of required corpora and lexicons, checks whether each exists locally, and downloads only those that are missing. This prevents redundant downloads in Docker/CI environments while ensuring first-run correctness.

### Formal Representation

Let $\mathcal{R} = \{(c_1, p_1), (c_2, p_2), \ldots, (c_n, p_n)\}$ be the set of required NLTK resources, where $c_i$ is the check path and $p_i$ is the package name.

The resource acquisition function $\text{ensure}$ is:

$$
\text{ensure}(\mathcal{R}) = \bigcup_{i=1}^{n} \text{acquire}(c_i, p_i)
$$

Where:

$$
\text{acquire}(c_i, p_i) =
\begin{cases}
\emptyset & \text{if } \texttt{nltk.data.find}(c_i) \text{ succeeds (resource cached)} \\
\texttt{nltk.download}(p_i) & \text{if } \texttt{LookupError} \text{ is raised (resource missing)}
\end{cases}
$$

### Idempotency Property

The lazy acquisition satisfies idempotency:

$$
\text{ensure}^n(\mathcal{R}) \equiv \text{ensure}^1(\mathcal{R}) \quad \forall n \geq 1
$$

Once all resources are cached locally, subsequent calls are no-ops (all checks succeed with $O(1)$ filesystem lookups). This is critical for containerized deployments where the constructor may be called multiple times across worker processes.

### Cold-Start vs. Warm-Start Cost Model

Let $D_i$ be the download cost for resource $i$ and $F$ be the filesystem check cost:

$$
\text{cost}_{cold} = \sum_{i=1}^{n} (F + D_i) \quad \text{(first run, all missing)}
$$

$$
\text{cost}_{warm} = \sum_{i=1}^{n} F = n \cdot F \quad \text{(subsequent runs, all cached)}
$$

The speedup factor from caching:

$$
\text{speedup} = \frac{\text{cost}_{cold}}{\text{cost}_{warm}} = \frac{n \cdot F + \sum D_i}{n \cdot F} = 1 + \frac{\sum D_i}{n \cdot F}
$$

For typical NLTK resources (each ~1-10MB, $F \approx 1\text{ms}$, $D_i \approx 1\text{s}$), the speedup is $\approx 1000\times$.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $\mathcal{R}$ | `NLTK_REQUIREMENTS` | `List[Tuple[str, str]]` | `quality.py:L26-L31` |
| $c_i$ | `check_path` | `str` | `quality.py:L39` |
| $p_i$ | `pkg_name` | `str` | `quality.py:L39` |
| $n$ | `len(NLTK_REQUIREMENTS)` | `int` = 4 | `quality.py:L26` |

### Complexity Analysis

- **Time (cold start):** $O(n \cdot D)$ — where $D$ is the download time per resource (network-bound)
- **Time (warm):** $O(n)$ — each `nltk.data.find()` is a local filesystem check
- **Space:** $O(1)$ — no additional in-memory state; resources stored on disk

---

## Algorithm 2: Text Quality Report Generation Pipeline

**Source:** [quality.py:L60-L112](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L60-L112)

### Description

The `generate_report` method implements a 4-stage pipeline: (1) input validation, (2) column mapping construction, (3) Evidently report execution with TextEvals preset, and (4) HTML serialization. The method takes a DataFrame of LLM logs, runs NLP-based quality evaluations (sentiment, text length, OOV ratio, etc.), and produces a self-contained HTML report.

### Formal Representation

Given a DataFrame $D$ with $N$ rows and a target text column $t$:

$$
\text{generate\_report}(D, t, p) =
\begin{cases}
\text{error} & \text{if } t \notin \text{columns}(D) \\
\text{save\_html}\Big(\text{Evidently.run}(D, \mathcal{M}_{text}), p\Big) & \text{otherwise}
\end{cases}
$$

Where:
- $\mathcal{M}_{text} = \texttt{TextEvals()}$ is the preset containing NLP metrics
- $p$ is the output file path

### TextEvals Metric Suite

The TextEvals preset internally computes a vector of NLP quality metrics:

$$
\mathcal{M}_{text}(D, t) = \Big\{\mu_{sent}(D_t), \; \mu_{len}(D_t), \; \mu_{oov}(D_t), \; \mu_{words}(D_t) \Big\}
$$

#### Metric 1: VADER Sentiment Score

$$
\mu_{sent}(D_t) = \frac{1}{N} \sum_{i=1}^{N} \text{VADER}(D_t^{(i)})
$$

Where $\text{VADER}(x)$ implements the **Valence Aware Dictionary and sEntiment Reasoner** algorithm:

$$
\text{VADER}(x) = \frac{\sum_{w \in x} v(w) \cdot m(w)}{\sqrt{\left(\sum_{w \in x} v(w) \cdot m(w)\right)^2 + \alpha}}
$$

Where:
- $v(w)$ is the valence score from the VADER lexicon ($v \in [-4, +4]$)
- $m(w)$ is the modifier score (negation, intensification, punctuation boosts)
- $\alpha = 15$ is a normalization constant
- Output is normalized to $[-1, +1]$ via the compound score formula

The compound score captures the overall sentiment polarity:
- $> 0.05$: Positive sentiment
- $< -0.05$: Negative sentiment
- Between: Neutral

#### Metric 2: Text Length Distribution

$$
\mu_{len}(D_t) = \frac{1}{N} \sum_{i=1}^{N} |D_t^{(i)}|
$$

With standard deviation for distribution analysis:

$$
\sigma_{len}(D_t) = \sqrt{\frac{1}{N-1} \sum_{i=1}^{N} (|D_t^{(i)}| - \mu_{len})^2}
$$

#### Metric 3: Out-of-Vocabulary (OOV) Ratio

$$
\mu_{oov}(D_t) = \frac{1}{N} \sum_{i=1}^{N} \frac{|\text{OOV}(D_t^{(i)})|}{|\text{tokens}(D_t^{(i)})|}
$$

The OOV detection uses the NLTK `words` corpus as a reference vocabulary $\mathcal{V}$:

$$
\text{OOV}(x) = \{w \in \text{tokens}(x) \mid w_{\text{lower}} \notin \mathcal{V}\}
$$

Where $|\mathcal{V}| \approx 236,736$ English words. A high OOV ratio indicates:
- Generated text contains hallucinated or nonsensical tokens
- Domain-specific jargon not in standard vocabulary
- Encoding errors or garbled output

#### Metric 4: Word Count Distribution

$$
\mu_{words}(D_t) = \frac{1}{N} \sum_{i=1}^{N} |\text{tokens}(D_t^{(i)})|
$$

Where tokenization uses whitespace splitting (Evidently default).

### Pipeline Stage Model

The 4-stage pipeline can be modeled as a function composition:

$$
\text{generate\_report} = \text{serialize} \circ \text{compute} \circ \text{map} \circ \text{validate}
$$

Each stage has distinct failure modes:

| Stage | Function | Failure Mode | Error Type |
|:---|:---|:---|:---|
| 1. Validate | $\text{validate}(D, t)$ | Column not found | `ValueError` |
| 2. Map | $\text{map}(t) \to CM$ | Invalid mapping | Evidently internal |
| 3. Compute | $\text{compute}(D, CM)$ | NLTK missing, memory | `RuntimeError` |
| 4. Serialize | $\text{serialize}(R, p)$ | Disk full, permissions | `RuntimeError` |

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $D$ | `df_logs` | `pd.DataFrame` | `quality.py:L62` |
| $t$ | `text_column` | `str` | `quality.py:L64` |
| $p$ | `output_path` | `str` | `quality.py:L63` |
| $\mathcal{M}_{text}$ | `TextEvals()` | `Report Preset` | `quality.py:L96` |
| $N$ | `len(df_logs)` | `int` | implicit |
| $D_t^{(i)}$ | `df_logs[text_column].iloc[i]` | `str` | implicit |
| $CM$ | `column_mapping` | `ColumnMapping` | `quality.py:L90-L93` |

### Complexity Analysis

- **Time:** $O(N \cdot L)$ — where $N$ is the number of rows and $L$ is the average text length (NLP metrics are linear in text length)
- **Space:** $O(N \cdot |\mathcal{M}|)$ — stores metric results for each row × each metric
- **I/O:** $O(R_{html})$ — HTML report size, typically $O(N)$ for embedded plots

---

## Algorithm 3: Column Validation with Diagnostic Error

**Source:** [quality.py:L79-L84](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L79-L84)

### Description

Before executing the expensive Evidently pipeline, the method performs a **fail-fast validation** that checks whether the target text column exists in the input DataFrame. If missing, it raises a `ValueError` with diagnostic information including all available column names.

### Formal Representation

$$
\text{validate}(D, t) =
\begin{cases}
\bot \text{ (raise ValueError with columns}(D)) & \text{if } t \notin \text{columns}(D) \\
\top \text{ (proceed)} & \text{if } t \in \text{columns}(D)
\end{cases}
$$

### Diagnostic Error Information Theory

The error message includes column names, providing diagnostic entropy:

$$
H_{diag} = \log_2(|\text{columns}(D)|) \quad \text{bits}
$$

This communicates the full search space to the user, enabling rapid correction. Without column names, the user would need to inspect the DataFrame manually — a $O(c)$ operation where $c$ is the number of columns.

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $D$ | `df_logs` | `pd.DataFrame` | `quality.py:L62` |
| $t$ | `text_column` | `str` | `quality.py:L64` |
| $\text{columns}(D)$ | `df_logs.columns` | `Index` | `quality.py:L80` |

### Complexity Analysis

- **Time:** $O(c)$ — where $c$ is the number of columns (membership check)
- **Space:** $O(c)$ — for the error message containing column names

---

## Algorithm 4: Exception-Safe Report Execution with Structured Logging

**Source:** [quality.py:L98-L111](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L98-L111)

### Description

The report execution is wrapped in a `try/except` block that catches any Evidently-internal exception and re-raises it as a `RuntimeError` with the original exception chained via `from exc`. This provides structured error propagation while preserving the full stack trace for debugging.

### Formal Representation

Let $R$ be the Evidently report computation and $E$ be any exception:

$$
\text{safe\_run}(D, p) =
\begin{cases}
p & \text{if } R(D) \text{ succeeds and } \text{save}(R, p) \text{ succeeds} \\
\text{raise RuntimeError}(E) & \text{if } \exists E \in \text{exceptions}(R(D) \cup \text{save}(R, p))
\end{cases}
$$

The exception chaining preserves causal information:

$$
\text{RuntimeError} \xleftarrow{\text{from}} E_{original}
$$

This creates a traceable error graph:

$$
\text{traceback} = [\text{RuntimeError}, E_{original}, E_{root\_cause}]
$$

### Logging Integration

The method uses structured logging at three levels:

| Level | Location | Content | Purpose |
|:---|:---|:---|:---|
| `info` | `quality.py:L77` | Report generation start | Audit trail |
| `info` | `quality.py:L106` | Success with output path | Confirmation |
| `error` | `quality.py:L110` | Failure with `exc_info=True` | Full traceback for debugging |

The `exc_info=True` flag ensures the complete stack trace is captured in structured logs, enabling correlation with monitoring systems (e.g., Sentry, Datadog).

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $R$ | `report` | `Report` | `quality.py:L96` |
| $D$ | `df_logs` | `pd.DataFrame` | `quality.py:L62` |
| $p$ | `output_path` | `str` | `quality.py:L63` |
| $E$ | `exc` | `Exception` | `quality.py:L109` |

### Complexity Analysis

- **Time:** $O(1)$ — only the exception handling overhead
- **Space:** $O(|\text{traceback}|)$ — stack trace storage

---

## Algorithm 5: Directory Provisioning for Report Output

**Source:** [quality.py:L87](file:///home/dell/PycharmProjects/Yantra/src/nikhil/yantra/domain/monitoring/quality.py#L87)

### Description

Before writing the HTML report, the method ensures the output directory exists using `os.makedirs` with `exist_ok=True`. The `or "."` clause handles the edge case where the output path has no directory component (writing to the current directory).

### Formal Representation

Let $p$ be the output path and $\text{dir}(p)$ be its directory component:

$$
\text{ensure\_dir}(p) =
\begin{cases}
\text{makedirs}(\text{dir}(p)) & \text{if } \text{dir}(p) \neq \emptyset \\
\text{no-op} & \text{if } \text{dir}(p) = \emptyset \text{ (current dir via ".")}
\end{cases}
$$

The `exist_ok=True` parameter ensures idempotency:

$$
\text{makedirs}^n(d, \text{exist\_ok=True}) \equiv \text{makedirs}^1(d, \text{exist\_ok=True}) \quad \forall n \geq 1
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | Type | Location |
|:---|:---|:---|:---|
| $p$ | `output_path` | `str` | `quality.py:L63` |
| $\text{dir}(p)$ | `os.path.dirname(output_path)` | `str` | `quality.py:L87` |

### Complexity Analysis

- **Time:** $O(d)$ — where $d$ is the depth of the directory path
- **Space:** $O(1)$ — filesystem-only operation

---

## Cross-Algorithm Dependency Graph

The 5 algorithms form a lifecycle pipeline:

$$
\text{\_\_init\_\_}() \to \{A_1\} \quad \text{(constructor)}
$$

$$
\text{generate\_report}() \to A_3 \to A_5 \to A_2 \to A_4 \quad \text{(report pipeline)}
$$

| Algorithm | Lifecycle Phase | Depends On | Called By |
|:---|:---|:---|:---|
| A1 (Lazy NLTK) | Constructor (one-time) | None | `__init__()` |
| A2 (Report Pipeline) | Report generation | A3, A4, A5 | Client code |
| A3 (Column Validation) | Pre-computation guard | None | A2 |
| A4 (Exception-Safe Execution) | Error handling wrapper | None | A2 |
| A5 (Directory Provisioning) | Pre-I/O guard | None | A2 |

---

## Aggregate Metric Quality Score

The TextEvals metrics can be combined into an aggregate quality score for LLM output:

$$
Q(D_t) = w_1 \cdot \text{norm}(\mu_{sent}) + w_2 \cdot \text{norm}(\mu_{len}) + w_3 \cdot (1 - \mu_{oov}) + w_4 \cdot \text{norm}(\mu_{words})
$$

Where:
- $w_i$ are configurable weights ($\sum w_i = 1$)
- $\text{norm}(x)$ maps values to $[0, 1]$
- $(1 - \mu_{oov})$ penalizes high out-of-vocabulary ratios

This aggregate score is not currently implemented but represents a natural extension for threshold-based alerting (see MON-GAP-005).
