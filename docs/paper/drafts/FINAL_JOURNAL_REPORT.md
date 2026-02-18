# Yantra: A Protocol-First Python Library for Composable MLOps Infrastructure

**Abstract**

The fragmentation of the MLOps ecosystem forces developers to choose between monolithic frameworks (e.g., ZenML, Kubeflow) that impose rigid workflows or ad-hoc glue code that becomes unmaintainable. This paper introduces **Yantra**, a Python library that applies a **Protocol-first architectural pattern** to MLOps infrastructure. By defining strict `Protocol` interfaces for core domains—Experiment Tracking, Orchestration, Model Monitoring, and Data Versioning—Yantra decouples application logic from specific backends (MLflow, Prefect, Evidently, DVC). We present a formal analysis of Yantra's four core modules, identifying 13 algorithmic formalizations and specific architectural contributions, including a novel dual-context decorator that bridges orchestration and observability. Our analysis classifies Yantra's system-level novelty as **incremental-to-novel**, positioning it as a lightweight, composable alternative to heavy frameworks.

---

## 1. Introduction

Machine Learning Operations (MLOps) lacks a standard interface definition language. Tools like MLflow, DVC, and Prefect provide excellent specific capabilities but lack a unified surface area, leading to "glue code" that tightly couples model code to infrastructure.

Yantra addresses this by introducing a **Protocol-First Architecture**. Instead of abstracting infrastructure via configuration (like ZenML's stack) or inheritance (like Metaflow's `FlowSpec`), Yantra uses Python's PEP 544 structural subtyping (`Protocol`) to define behavior. This allows developers to write code against abstract interfaces (`IExperimentTracker`, `IDataVersionControl`) that can be satisfied by any compliant backend implementation.

This report analyzes Yantra's four primary modules:
1. **Observability:** Protocol-decoupled tracking with LLM tracing support.
2. **Orchestration:** Unified workflow execution with auto-instrumentation.
3. **Monitoring:** Text-first quality metrics for GenAI systems.
4. **Data Versioning:** Infrastructure-as-Code patterns for data logistics.

---

## 2. System Architecture

Yantra follows a consistent **3-Tier Architecture** across all domains, enabling predictable extension and uniform testing strategies.

### 2.1 The 3-Tier Pattern

| Tier | Role | Example Component |
|:---|:---|:---|
| **Tier 1: Protocol** | Defines the *Interface* (What) | `IExperimentTracker`, `IDataVersionControl` |
| **Tier 2: Implementation** | Provides the *Behavior* (How) | `MLflowTracker`, `DVCDataTracker` |
| **Tier 3: integration** | Unifies components (Glues) | `submodule exports`, `YantraContext` |

### 2.2 Cross-Module Dependencies

The system adheres to the **Stable Dependencies Principle**. Unstable consumer-facing modules (`orchestration`, `data_versioning`) depend on stable interface definitions (`observability`, `utils`).

- **Key Synergy:** The `orchestration` module depends on `observability` interfaces to provide auto-instrumentation.
- **Isolation:** `monitoring` and `data_versioning` operate as standalone modules, preventing a "monolithic core" antipattern.

---

## 3. Module Analysis

### 3.1 Observability Module
*Focus: Experiment Tracking & LLM Tracing*

**Key Contribution:** A backend-agnostic `IExperimentTracker` protocol (11 methods) that abstracts both metric logging and complex LLM trace hierarchies.

*   **Algorithms:**
    *   **Adaptive Span Hierarchy:** $O(1)$ construction of nested trace spans.
    *   **Arena Evaluation:** Matrix-based comparison of model outputs ($\mathbf{C}_{k \times |\phi|}$).
*   **Novelty:** INCREMENTAL. The decoupled observability pattern allows swapping MLflow for Weights & Biases without changing model code.
*   **Critical Gaps:** Lack of unit tests (OBS-GAP-001) and Protocol impurity (importing `mlflow`).

### 3.2 Orchestration Module
*Focus: Workflow Execution*

**Key Contribution:** The `@yantra_task` decorator, which creates a "Dual-Context" execution environment. It simultaneously registers a task with Prefect (for orchestration) and opens an MLflow span (for observability) via a single annotation.

*   **Algorithms:**
    *   **Dual-Context Decoration:** $f' = \text{prefect.task} \circ \text{mlflow\_span\_wrap}(f)$.
    *   **Signature Introspection:** Zero-config capture of function arguments as trace inputs.
*   **Novelty:** INCREMENTAL. Bridges the "Instrumentation Gap" between workflow schedulers and experiment trackers.

### 3.3 Monitoring Module
*Focus: Data & Model Quality*

**Key Contribution:** A text-first quality monitoring pipeline designed for GenAI, utilizing `Evidently` for rigorous text stat calculation (Sentiment, OOV ratio, Length).

*   **Algorithms:**
    *   **Lazy Resource Acquisition:** JIT downloading of NLTK corpora to optimize container startup.
    *   **TextEvals Pipeline:** Formalized metrics for text quality ($\mu_{sent}, \mu_{oov}$).
*   **Novelty:** INCREMENTAL (Low Confidence). The "text-first" approach is timely, but the module lacks drift detection (critical gap).

### 3.4 Data Versioning Module
*Focus: Dataset Logistics*

**Key Contribution:** A clean architectural separation between **Infrastructure Provisioning** (`DVCSetup`) and **Workflow Execution** (`DVCDataTracker`).

*   **Algorithms:**
    *   **Idempotent Provisioning:** 3-way HTTP status dispatch for safe S3 bucket creation.
    *   **Defensive Tracking:** Auto-creation of `.gitkeep` sentinels to prevent DVC failures on empty directories.
*   **Novelty:** INCREMENTAL (Medium). The separation of concerns is a robust architectural pattern often missing in DVC scripts.

---

## 4. Discussion & Limitations

### 4.1 Protocol Compliance
While all modules define Protocols, implementation purity varies. `IExperimentTracker` imports `mlflow`, violating the clean separation of interface and implementation. Future work must strictly remove external dependencies from the Protocol tier.

### 4.2 Research Gaps (Aggregate)
We identified **29 research gaps** across the system. The most critical impediments to publication are:
1.  **Testing:** Zero unit tests across 3 of 4 modules.
2.  **Security:** Credentials stored in YAML config files (Data Versioning).
3.  **Completeness:** Missing drift detection in Monitoring.

### 4.3 Comparison with Frameworks
Unlike **ZenML** (Pipeline-first) or **Metaflow** (DAG-first), Yantra is **Library-first**. It does not own the `main` execution thread. This composability allows teams to adopt Yantra's "Observability" module without being forced to use its "Orchestration" module.

---

## 5. Conclusion

Yantra demonstrates that **Protocol-based abstraction** is a viable and superior architectural pattern for Python MLOps infrastructure compared to monolithic frameworks. By enforcing strict interfaces, it enables testing, swapping, and maintenance of infrastructure code with the same rigor as application code. While the current implementation requires stronger testing and drift detection capabilities, the architectural foundation provides a novel contribution to the field of Machine Learning Engineering.

---

*Generated by Lutapi (Journal Master Skill) — Phase 3 Synthesis*
