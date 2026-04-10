<!-- GSD:project-start source:PROJECT.md -->
## Project

**Project: Yantra**

Yantra is a standalone MLOps library that wraps Essential MLOps tools (DVC, MLflow, Prefect, Evidently) into a unified, protocol-based interface. Users wrap Yantra only - no need to use individual tools directly. Designed for agentic AI systems and research purposes.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.8+ - Core language (per README requirement)
- None detected
## Runtime
- Standard Python runtime
- Virtual environment required (see README documentation)
- pip (with pyproject.toml)
- No lockfile detected
## Frameworks
- `dvc-s3` 3.0.1 - Data Version Control with S3 backend
- `mlflow` 3.6.0 - Experiment tracking
- `prefect` 3.6.4 - Workflow orchestration
- `evidently` 0.7.17 - Model monitoring
- `pandas` 2.3.2 - Data manipulation
- `numpy` 2.2.6 - Numerical computing
- `nltk` 3.9.2 - Natural language processing
- `boto3` 1.34.0 - AWS SDK for Python
- `PyYAML` 6.0.3 - YAML configuration parsing
- `python-dotenv` 1.2.1 - Environment variable loading
- `watchfiles` 1.1.1 - File watching for development
## Key Dependencies
- `Nibandha[export]` - Local dependency (file:// URL), custom framework
- `dvc-s3` 3.0.1 - DVC configured for S3/MinIO storage
- `mlflow` 3.6.0 - Experiment tracking server
- `prefect` 3.6.4 - Workflow orchestration engine
- `evidently` 0.7.17 - Model quality monitoring
- `boto3` 1.34.0 - S3/MinIO connectivity
- `pandas` 2.3.2 - Data handling
- `PyYAML` 6.0.3 - Configuration files
- Not detected in dependencies (pytest mentioned in README but not in pyproject.toml)
- setuptools (via `[tool.setuptools]` in pyproject.toml)
- Package location: `src/nikhil` (custom package-dir mapping)
## Configuration
- `.env` files supported via `python-dotenv`
- YAML configuration files (e.g., `config/mlops_config.yaml`)
- Typical env vars: `GEMINI_API_KEY`, AWS credentials, database connection strings
- `pyproject.toml` - Modern Python package configuration
- Package structure: Single namespace `nikhil` mapped to `src/nikhil`
## Platform Requirements
- Python 3.8 or higher
- Git
- Docker & Docker Compose (for infrastructure services)
- Virtual environment required
- Python runtime
- Running infrastructure (MinIO, PostgreSQL, MLflow, Prefect)
- S3-compatible storage (MinIO or AWS S3)
## Docker Infrastructure Services
- MinIO (S3 storage) - Port 9000/9001
- PostgreSQL 15 - Port 5432
- MLflow v3.6.0 - Port 5000
- Prefect v3 (latest) - Port 4200
- No dedicated Evidently service (runs as Python library)
- No Redis/caching service
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- `snake_case` - All lowercase with underscores
- `PascalCase` - Initial capitals, no underscores
- `snake_case` - All lowercase
- `PascalCase` prefixed with `I`
- `SCREAMING_SNAKE_CASE` - All uppercase with underscores
- `_snake_case` - Single underscore prefix
## Code Style
- Uses `black` for code formatting (invoked via `black src/` in README)
- 4-space indentation
- Uses Python type hints with `Optional`, `Dict`, `List` from `typing`
- Uses Google-style docstrings for documentation
## Import Organization
- Uses relative imports (`from .module_name import ClassName`)
- Avoids absolute imports within the package
- Standard library imports first: `import subprocess`, `from pathlib import Path`
- Third-party imports second: `import boto3`, `import mlflow`
- Local package imports last: `from yantra.utils import YamlUtils`
- Avoids aliasing standard library modules
- Uses `Union[]` for type hints (e.g., `Union[str, Path]`)
## Module Design
- Explicitly defines `__all__` for public API
- External boundaries use `Protocol` classes with `@runtime_checkable` decorator
- Uses class variables for singleton context
## Error Handling
- Defines custom exception classes inheriting from `Exception`
- Provides descriptive error messages including context
## Logging
- Uses `logger.info()`, `logger.debug()`, `logger.error()`
- Includes exception info with `exc_info=True` for errors
## Function Design
- Type-hinted parameters with defaults where appropriate
- Configuration passed as file paths (YAML)
- Returns explicit types
- Uses decorators for cross-cutting concerns
- Uses `@contextlib.context-manager` for span-based operations
## Configuration Management
- Configuration loaded from YAML files using `YamlUtils`
- Safe loading with `yaml_safe_load()`
- Safe dumping with `yaml_safe_dump()`
## Testing Conventions
## Documentation Comments
- Single-line comments describe file contents: `# src/nikhil/yantra/domain/data_versioning/dvc_setup.py`
- Uses decorative section headers
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- **Interface-First Design**: Protocols (Python's structural typing) define contracts before implementations
- **Swappable Implementations**: Domain logic depends on abstractions, not concrete tools
- **Centralized Context**: Singleton-style context (`YantraContext`) manages runtime state
- **Configuration-Driven**: All infrastructure setup via YAML configuration files
## Layers
### Protocol Layer (Interfaces)
- Purpose: Define contracts for domain operations
- Location: `src/nikhil/yantra/domain/*/ *_protocol.py`
- Contains: Abstract protocol definitions with `@runtime_checkable`
- Depends on: Python typing module only
- Used by: All implementation modules
- `IDataVersionControl` (`data_versioning/data_version_protocol.py`)
- `IExperimentTracker` (`observability/experiment_tracker_protocol.py`)
- `IModelMonitor` (`monitoring/model_monitor_protocol.py`)
### Domain Layer (Implementations)
- Purpose: Provide concrete implementations of protocols
- Location: `src/nikhil/yantra/domain/[module]/`
- Contains: Production-ready implementations
- Depends on: Protocol layer + external libraries
- Used by: Orchestration layer + user code
| Module | Implementation | File |
|--------|----------------|------|
| data_versioning | DVCDataTracker | `domain/data_versioning/dvc_tracker.py` |
| data_versioning | DVCSetup | `domain/data_versioning/dvc_setup.py` |
| observability | MLflowTracker | `domain/observability/mlflow_tracker.py` |
| observability | ModelArena | `domain/observability/arena.py` |
| monitoring | EvidentlyQualityMonitor | `domain/monitoring/quality.py` |
| orchestration | yantra_task decorator | `domain/orchestration/prefect_utils.py` |
### Orchestration Layer
- Purpose: Combine domain operations into workflow tasks
- Location: `src/nikhil/yantra/domain/orchestration/`
- Contains: Prefect task decorators, context management
- Depends on: Domain layer + Prefect
- Used by: Workflow pipelines
- `YantraContext` (`domain/orchestration/context.py`) - Global tracker singleton
- `yantra_task` (`domain/orchestration/prefect_utils.py`) - Dual-purpose decorator (Prefect + MLflow)
### Utility Layer
- Purpose: Shared helper functions
- Location: `src/nikhil/yantra/utils/`
- Contains: YAML loading, configuration parsing
- Depends on: Standard library only
## Data Flow
### Configuration Flow
```
```
### Data Versioning Flow
```
```
### Observability Flow
```
```
### Monitoring Flow
```
```
## Key Abstractions
- Purpose: Abstract data versioning operations
- Examples: `DVCDataTracker`
- Pattern: Protocol with implementation
- Purpose: Abstract experiment tracking + LLM tracing
- Examples: `MLflowTracker`
- Pattern: Protocol with MLflow-specific features
- Purpose: Abstract model quality monitoring
- Examples: `EvidentlyQualityMonitor`
- Pattern: Protocol with swappable backends (Evidently, DeepChecks, Whylogs)
- Purpose: LLM comparison framework
- Location: `domain/observability/arena.py`
- Pattern: MLflow Evaluate with LLM-as-a-Judge metrics
## Entry Points
- Location: `config/mlops_config.yaml`
- Triggers: YAML loading via `YamlUtils`
- Responsibilities: Define paths, credentials, service endpoints
- DVC: `DVCSetup(config_path).setup()`
- Tracking: `YantraContext.set_tracker(MLflowTracker(...))`
- Monitoring: `EvidentlyQualityMonitor()`
- Location: `@yantra_task` decorator
- Triggers: Function decorated with `@yantra_task`
- Responsibilities: Register as Prefect task + wrap in MLflow span
## Error Handling
- `YantraDVCError` - Wraps subprocess DVC errors
- `FileNotFoundError` - Missing config files
- `yaml.YAMLError` - Malformed YAML
- Context manager fallbacks in `mlflow_tracker.py`
- `yantra_task` decorator automatically captures and logs exceptions to MLflow trace before re-raising
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
