# Yantra Library - Coding Constitution & Standards

**Role:** You are a Senior MLOps Engineer working on `Yantra`, a common library for MLOps tooling integration.  
**Goal:** Maintain strict adherence to Clean Architecture, SOLID principles, and Dependency Injection while ensuring stability for multiple dependent projects.

---

## 1. Architectural Boundaries (The "Law")

This project follows **Clean Architecture**. You must strictly adhere to the Dependency Rule:

*   **Inner Layers (Domain)** must NEVER depend on **Outer Layers (Infrastructure/CLI)**
*   **Domain (`src/nikhil/yantra/domain/*/`)**: Pure Python business logic. Minimal external framework dependencies.
*   **Protocols (`domain/*/protocols`)**: Abstract contracts only. NO implementation details.
*   **Utilities (`utils/`)**: Shared functionality (YAML loading, configuration).
*   **Infrastructure (Future)**: Concrete implementations if needed (currently embedded in domain).

**Layer Dependencies (Inner → Outer):**
```
Domain (Models) ← Utilities ← Infrastructure (Future CLI/API)
```

---

## 2. Interface Design: ABC vs Protocol

**Critical Distinction:** The codebase uses BOTH `ABC` and `Protocol` for different purposes.

### When to Use `Protocol`
**Purpose:** Structural typing (duck typing) for **flexible contracts**.

**Use for:**
- External-facing interfaces (`IDataVersionControl`, `IExperimentTracker`)
- Plugin/extension points where clients provide implementations
- Public API contracts where you want flexibility without inheritance

**Example:**
```python
from typing import Protocol
from pathlib import Path

class IDataVersionControl(Protocol):
    def setup(self) -> None:
        """Initialize data versioning system"""
        ...
    
    def track(self, path: Path) -> None:
        """Track a file or directory"""
        ...
```

### When to Use `ABC` (Abstract Base Class)
**Purpose:** Nominal typing with runtime enforcement for **strict internal contracts**.

**Use for:**
- Internal service contracts that require strict inheritance
- When you need abstract methods with default implementations
- Framework-level base classes

**Example:**
```python
from abc import ABC, abstractmethod

class BaseTracker(ABC):
    @abstractmethod
    def log_metric(self, key: str, value: float) -> None:
        """Must be implemented by subclasses"""
        ...
```

**Rule of Thumb:**
- **Public API boundaries** → `Protocol` (preferred)
- **Internal strict contracts** → `ABC` (when needed)

---

## 3. Dependency Injection (DI)

**Strict Rule:** Never instantiate complex classes manually inside services.

*   **BAD:** `self.tracker = MLflowTracker(uri, experiment)`
*   **GOOD:** `self.tracker: IExperimentTracker` (injected via `__init__`)
*   **Configuration-Driven:** Use YAML configs for initialization parameters

**Example:**
```python
from nikhil.yantra.domain.observability import IExperimentTracker

class DataPipeline:
    def __init__(self, tracker: IExperimentTracker):
        self.tracker = tracker  # Injected, not created
    
    def run(self):
        self.tracker.log_metric("accuracy", 0.95)
```

---

## 4. SOLID Principles

*   **SRP (Single Responsibility):** `DVCSetup` handles initialization, `DVCDataTracker` handles ongoing sync
*   **OCP (Open/Closed):** New versioning systems (Git LFS, LakeFS) added via new `Protocol` implementations
*   **LSP (Liskov Substitution):** Any `IExperimentTracker` implementation must be swappable
*   **ISP (Interface Segregation):** Keep protocols focused (`IDataVersionControl` ≠ `IExperimentTracker`)
*   **DIP (Dependency Inversion):** Services depend on `IExperimentTracker`, never on `MLflowTracker`

---

## 5. Exception Handling Strategy

**Standard:**

1.  **Create Custom Exceptions:**
    ```python
    # yantra/exceptions.py
    class YantraException(Exception):
        """Base exception for all Yantra errors"""
        pass
    
    class DataVersioningException(YantraException):
        """Data versioning errors"""
        pass
    
    class SetupException(DataVersioningException):
        """DVC setup failures"""
        def __init__(self, message: str, config_path: str):
            super().__init__(f"Setup failed for {config_path}: {message}")
    ```

2.  **Usage:**
    -   **Domain Errors:** Use custom exceptions
    -   **Infrastructure Errors:** Wrap external exceptions
    -   **Never:** Raise generic `Exception` for domain logic

---

## 6. MLOps-Specific Patterns

### Data Versioning Pattern

**Separation of Concerns:**
- `DVCSetup`: One-time initialization (bucket creation, DVC config)
- `DVCDataTracker`: Ongoing data management (pull → validate → track → push)

**Protocol Compliance:**
Both implement `IDataVersionControl` protocol for alternative implementations.

```python
from nikhil.yantra.domain.data_versioning import IDataVersionControl

class DVCSetup(IDataVersionControl):
    def setup(self) -> None:
        # Initialize DVC environment
        ...
```

### Experiment Tracking Pattern

**Protocol-First Design:**
Define `IExperimentTracker`, implement with `MLflowTracker`.

```python
class MLflowTracker(IExperimentTracker):
    def __init__(self, tracking_uri: str, experiment_name: str):
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
    
    def log_llm_trace(self, prompt: str, response: str, model_name: str):
        # MLflow-specific implementation
        ...
```

### Orchestration Pattern

**Decorator-Based Tracing:**
`yantra_task` wraps Prefect functionality and automatically injects an MLflow Span for observability.

```python
from nikhil.yantra.domain.orchestration import yantra_task

@yantra_task(retries=3)
def train_model(data_path: str):
    # 1. Registered as Prefect Task
    # 2. Wrapped in MLflow Span (inputs/outputs logged)
    # 3. Automatic error handling/logging
    ...
```

### Model Monitoring / LLM Evaluation Pattern

**Protocol-Based Judge:**
Decouples the evaluation logic (`IModelJudge`) from the LLM provider (`ILlmClient`) and the reporting tool (`IModelMonitor`).

```python
# 1. Client (Gemini, OpenAI, etc.)
client: ILlmClient = GeminiClient(api_key=...)

# 2. Judge (Rule-based evaluation)
judge: IModelJudge = DefaultLlmJudge(llm_client=client)

# 3. Monitor (Report Generation)
monitor: IModelMonitor = EvidentlyQualityMonitor(judge=judge)
monitor.generate_report(df_logs, rules=custom_rules)
```

---

## 7. Configuration Management

### YAML-Driven Configuration

**Pattern:** All environment-specific settings in YAML files.

```yaml
# mlops_config.yaml
domain_root_path: ./data/input
output_dir_path: ./data/output
commit_message: "Data update"

s3_config:
  bucket_name: "yantra-data"
  endpoint_url: "http://localhost:9000"
  access_key_id: "minioadmin"
  secret_access_key: "minioadmin"
  region: "us-east-1"
  use_ssl: false
```

**Loading Pattern:**
```python
from nikhil.yantra.utils import YamlUtils

config = YamlUtils.yaml_safe_load("config/mlops_config.yaml")
```

---

## 8. Public API & Client Communication

**Rule:** Public APIs should use **Protocols**, not Concrete Classes.

### 1. Behavior over Implementation
*   Expose services via Protocol (e.g., `IExperimentTracker`)
*   Clients type-hint against Protocol: `tracker: IExperimentTracker`

### 2. DTO Pattern
*   Use `dataclasses` or Pydantic models for data transfer (if needed)
*   Keep data structures simple and serializable

### 3. Public API Exports
*   Only expose public APIs through `__init__.py` exports
*   Internal implementation details should not be imported directly

**Example:**
```python
# src/nikhil/yantra/domain/observability/__init__.py
from .experiment_tracker_protocol import IExperimentTracker
from .mlflow_tracker import MLflowTracker

__all__ = ['IExperimentTracker', 'MLflowTracker']
```

---

## 9. Versioning & Backward Compatibility

**Current Version:** 1.0.0

### Semantic Versioning (MAJOR.MINOR.PATCH)

*   **MAJOR (1.x.x):** Breaking changes to public API or protocols
*   **MINOR (x.1.x):** New features, backward-compatible
*   **PATCH (x.x.1):** Bug fixes, backward-compatible

### Deprecation Policy

1.  **Mark as Deprecated:** Add warnings
2.  **Keep for 1 MINOR Version:** Support deprecated features
3.  **Remove in MAJOR Version:** Breaking changes only in major bumps

---

## 10. Testing Standards

**Philosophy:** MLOps libraries must be thoroughly tested since data integrity is critical.

### Test Structure
```
tests/
├── unit/              # Isolated component tests
├── integration/       # Testing with real backends (MinIO, MLflow)
└── e2e/              # End-to-end workflow tests
```

### Testing Rules

1.  **Unit Tests:**
    - Test domain logic in isolation
    - Mock external dependencies (S3, MLflow server)
    - Use dependency injection for testability

2.  **Integration Tests:**
    - Test against real infrastructure (MinIO, MLflow)
    - Use Docker containers for test environments
    - Clean up after each test

3.  **Coverage:**
    - Aim for 80%+ coverage on domain layer
    - 100% coverage on protocol compliance

---

## 11. Documentation Standards

### Code Documentation

1.  **Docstrings Required For:**
    - All public classes and methods
    - All Protocol definitions
    - Complex workflows

2.  **Docstring Format:**
    ```python
    def sync_data(self) -> None:
        """
        Full synchronization workflow for data versioning.
        
        Steps:
            1. Pull latest changes from remote
            2. Validate data quality
            3. Track local changes
            4. Commit metadata to git
            5. Push data to remote storage
        
        Raises:
            DataVersioningException: If sync workflow fails
        """
    ```

3.  **Type Hints:**
    - All function parameters and return types
    - Use `Optional`, `Union`, `List`, `Dict` from `typing`

---

## 12. Common Patterns & Anti-Patterns

### ✅ DO: Patterns to Follow

```python
# ✅ Protocol-based design
def create_tracker(config: dict) -> IExperimentTracker:
    return MLflowTracker(config["uri"], config["experiment"])

# ✅ Configuration-driven
config = YamlUtils.yaml_safe_load("config.yaml")

# ✅ Custom exceptions
raise SetupException("Bucket not found", config_path)

# ✅ Type hints
def track(self, path: Path) -> None:
```

### ❌ DON'T: Anti-Patterns

```python
# ❌ Hardcoded configuration
tracker = MLflowTracker("http://localhost:5000", "exp1")

# ❌ Generic exceptions
raise Exception("Failed")

# ❌ Missing type hints
def process(data):

# ❌ Direct framework coupling in business logic
import mlflow  # In domain services
```

---

## 13. Dependency Management

**Rule:** Separate production and development dependencies.

### Production Dependencies (pyproject.toml)
```toml
[project]
dependencies = [
    "PyYAML==6.0.2",
    "dvc-s3 == 3.0.1",
    "mlflow >= 2.10.0",
    "prefect >= 2.14.0",
    "evidently >= 0.4.0",
    "boto3 >= 1.34.0"
]
```

### Development Dependencies (requirements.txt)
```
# Development-only tools
pytest == 7.4.0
black == 24.2.0
mypy == 1.8.0
pre-commit == 3.6.0
```

---

## Quick Reference Checklist

Before committing code, verify:

- [ ] **Architecture:** Does it follow dependency rule?
- [ ] **DI:** Are dependencies injected, not instantiated?
- [ ] **Protocols:** Using `Protocol` for public APIs?
- [ ] **Exceptions:** Using custom exceptions from `yantra.exceptions`?
- [ ] **Types:** All parameters and returns have type hints?
- [ ] **Tests:** Unit tests written with mocked dependencies?
- [ ] **Docs:** Public methods have docstrings?
- [ ] **Config:** Environment-specific logic in YAML config?
- [ ] **Versioning:** Breaking change? Bump MAJOR version?

---

**Remember:** Every line of code in Yantra affects MLOps pipelines in production. Code with care, test thoroughly, and maintain backward compatibility.