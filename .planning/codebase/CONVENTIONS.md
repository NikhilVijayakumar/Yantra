# Coding Conventions

**Analysis Date:** 2026-04-10

## Naming Patterns

**Modules/Packages:**
- `snake_case` - All lowercase with underscores
  - Example: `src/nikhil/yantra/domain/data_versioning/dvc_setup.py`

**Classes:**
- `PascalCase` - Initial capitals, no underscores
  - Example: `DVCSetup`, `MLflowTracker`, `EvidentlyQualityMonitor`

**Functions/Methods:**
- `snake_case` - All lowercase
  - Example: `yaml_safe_load()`, `_create_directories()`

**Protocol Interfaces:**
- `PascalCase` prefixed with `I`
  - Example: `IDataVersionControl`, `IExperimentTracker`, `IModelMonitor`

**Constants:**
- `SCREAMING_SNAKE_CASE` - All uppercase with underscores
  - Example: `NLTK_REQUIREMENTS` in `quality.py`

**Private Methods:**
- `_snake_case` - Single underscore prefix
  - Example: `_run_command()`, `_ensure_nltk_resources()`

## Code Style

**File Header Convention:**
Every source file should include a relative path comment at the top:
```python
# src/nikhil/yantra/domain/data_versioning/dvc_setup.py
```

**Formatting:**
- Uses `black` for code formatting (invoked via `black src/` in README)
- 4-space indentation

**Type Annotations:**
- Uses Python type hints with `Optional`, `Dict`, `List` from `typing`
  - Example: `def __init__(self, config_path: str):` and `def yaml_safe_load(file_path: Union[str, Path]) -> Dict[str, Any]:`

**Docstrings:**
- Uses Google-style docstrings for documentation
  - Example from `yaml_utils.py`:
  ```python
  @staticmethod
  def yaml_safe_load(file_path: Union[str, Path]) -> Dict[str, Any]:
      """
      Safely load a YAML configuration file.
      
      Args:
          file_path: Path to the YAML file (string or Path object)
          
      Returns:
          Dictionary containing the parsed YAML content
          
      Raises:
          FileNotFoundError: If the YAML file doesn't exist
          yaml.YAMLError: If the YAML file is malformed
      """
  ```

## Import Organization

**Package Structure:**
```
src/nikhil/yantra/
├── domain/
│   ├── data_versioning/
│   ├── observability/
│   ├── orchestration/
│   └── monitoring/
└── utils/
```

**Import Order in `__init__.py`:**
1. **Imports first** - Interface/Protocol definitions
2. **Setup second** - Setup classes
3. **Implementation last** - Tracker classes (since they depend on interfaces)
   - Example from `data_versioning/__init__.py`:
   ```python
   # 1. Import Interfaces FIRST
   from .data_version_protocol import IDataVersionControl

   # 2. Import Setup
   from .dvc_setup import DVCSetup, YantraDVCError

   # 3. Import Tracker LAST (since it depends on the others)
   from .dvc_tracker import DVCDataTracker
   ```

**Relative Imports:**
- Uses relative imports (`from .module_name import ClassName`)
- Avoids absolute imports within the package

**External Imports:**
- Standard library imports first: `import subprocess`, `from pathlib import Path`
- Third-party imports second: `import boto3`, `import mlflow`
- Local package imports last: `from yantra.utils import YamlUtils`

**Aliasing:**
- Avoids aliasing standard library modules
- Uses `Union[]` for type hints (e.g., `Union[str, Path]`)

## Module Design

**Barrel Files (`__init__.py`):**
- Explicitly defines `__all__` for public API
  - Example: `__all__ = ["IDataVersionControl", "DVCSetup", "DVCDataTracker", "YantraDVCError"]`

**Protocol-Based Design:**
- External boundaries use `Protocol` classes with `@runtime_checkable` decorator
  - Example from `data_version_protocol.py`:
  ```python
  @runtime_checkable
  class IDataVersionControl(Protocol):
      """Protocol for data versioning systems."""
  ```

**Singleton Pattern:**
- Uses class variables for singleton context
  - Example from `context.py`:
  ```python
  class YantraContext:
      _tracker: Optional[IExperimentTracker] = None

      @classmethod
      def set_tracker(cls, tracker: IExperimentTracker):
          cls._tracker = tracker
  ```

## Error Handling

**Custom Exceptions:**
- Defines custom exception classes inheriting from `Exception`
  - Example: `class YantraDVCError(Exception): pass`

**Error Messages:**
- Provides descriptive error messages including context
  - Example: `raise YantraDVCError(f"Configuration file not found at: {self.config_path}")`

## Logging

**Framework:** Uses Python's standard `logging` module

**Logger Initialization:**
```python
import logging
logger = logging.getLogger(__name__)
```

**Logging Patterns:**
- Uses `logger.info()`, `logger.debug()`, `logger.error()`
- Includes exception info with `exc_info=True` for errors

## Function Design

**Function Parameters:**
- Type-hinted parameters with defaults where appropriate
- Configuration passed as file paths (YAML)
- Returns explicit types

**Decorator Pattern:**
- Uses decorators for cross-cutting concerns
  - Example: `@yantra_task` decorator wraps Prefect tasks with MLflow tracing

**Context Managers:**
- Uses `@contextlib.context-manager` for span-based operations
  - Example: `def start_span(self, name: str, inputs: Optional[Dict] = None)`

## Configuration Management

**YAML-Driven:**
- Configuration loaded from YAML files using `YamlUtils`
- Safe loading with `yaml_safe_load()`
- Safe dumping with `yaml_safe_dump()`

**Configuration Pattern:**
```python
self.config = YamlUtils.yaml_safe_load(config_path)
self.root_dir = Path.cwd()
```

## Testing Conventions

**Test Framework:** `pytest` (referenced in README - `pytest`)

**Test Commands:**
```bash
pytest              # Run all tests
black src/         # Code formatting
mypy src/          # Type checking
```

## Documentation Comments

**Comment Headers:**
- Single-line comments describe file contents: `# src/nikhil/yantra/domain/data_versioning/dvc_setup.py`

**Section Comments:**
- Uses decorative section headers
  ```python
  # -------------------------------------------------------------------------
  # Internal Helpers
  # -------------------------------------------------------------------------
  ```

---

*Convention analysis: 2026-04-10*