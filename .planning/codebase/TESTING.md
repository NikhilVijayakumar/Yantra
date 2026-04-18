# Testing Patterns

**Analysis Date:** 2026-04-10

## Test Framework

**Runner:** `pytest` (declared in README.md)
- Version: Not explicitly specified in configuration
- Config: No dedicated `pytest.ini` or `conftest.py` at project root

**Assertion Library:** standard pytest assertions

**Run Commands:**
```bash
pytest              # Run all tests (as per README.md)
```

Note: Test execution is documented in README but no test files exist in the project.

## Test File Organization

**Location:** No dedicated test directory exists

**Current State:**
- No test files found in project
- No `tests/` directory
- No `*_test.py` or `test_*.py` files

**Pattern to Follow:** Testing follows pytest discovery patterns:
- `tests/` directory at project root OR
- Co-located test files with `test_*.py` / `*_test.py` naming

## Test Structure

**Expected Structure** (based on best practices):
```
tests/
├── __init__.py
├── domain/
│   ├── data_versioning/
│   │   └── test_dvc_setup.py
│   ├── observability/
│   │   └── test_mlflow_tracker.py
│   ├── orchestration/
│   │   └── test_prefect_utils.py
│   └── monitoring/
│       └── test_quality.py
└── utils/
    └── test_yaml_utils.py
```

## Test Fixtures

**Available Fixtures:**
- Template available in `.agent/skills/test-scaffolder/resources/pytest_conftest.py`

**Example Fixture Pattern:**
```python
import pytest
import shutil
from pathlib import Path

@pytest.fixture
def project_env(tmp_path):
    """
    Standard fixture for E2E tests.
    Creates a sandboxed .Amsha directory in a temporary path.
    """
    env_path = tmp_path / ".Amsha"
    env_path.mkdir()
    yield env_path
    # Teardown: Environment is automatically cleaned up by tmp_path
```

**Recommended Fixtures for Yantra:**
- `mlops_config` - Mock YAML configuration
- `temp_data_dir` - Temporary directory for DVC operations
- `mock_s3_client` - Mock boto3 S3 client
- `mock_mlflow_tracker` - Mock MLflow tracker

## Mocking

**Framework:** Python's `unittest.mock` (standard library)

**What to Mock:**
- External services: boto3 S3 operations, DVC CLI commands
- MLflow API calls
- Prefect task execution
- Evidently report generation
- Network calls (S3, MLflow server)

**What NOT to Mock:**
- Internal business logic
- Configuration parsing (unless file I/O is tested)
- Utility functions being tested directly

**Mocking Pattern Example:**
```python
from unittest.mock import Mock, patch

@patch('boto3.client')
def test_ensure_bucket_exists(mock_boto):
    # Arrange
    mock_s3 = Mock()
    mock_boto.return_value = mock_s3
    
    # Act
    setup = DVCSetup(config_path="config/mlops_config.yaml")
    setup._ensure_bucket_exists()
    
    # Assert
    mock_s3.head_bucket.assert_called_once()
```

## Fixtures and Factories

**Test Data:**
- Use temporary directories (`tmp_path` fixture)
- Mock YAML config files
- Sample DataFrames for monitoring tests

**Location:**
- Store fixture data in `tests/fixtures/` or use `tmp_path`

## Unit Testing Scope

**Data Versioning (`data_versioning`):**
- `DVCSetup` - Bucket creation, DVC configuration, directory creation
- `DVCDataTracker` - Sync workflow, data validation

**Experiment Tracking (`observability`):**
- `MLflowTracker` - Metric logging, parameter logging, span management
- `ModelArena` - LLM comparison logic

**Orchestration (`orchestration`):**
- `yantra_task` - Decorator behavior, retry logic, span wrapping

**Monitoring (`monitoring`):**
- `EvidentlyQualityMonitor` - Report generation, NLTK resource management

**Utilities (`utils`):**
- `YamlUtils` - Safe loading and dumping of YAML files

## Integration Testing

**Infrastructure Dependencies:**
- Requires Docker services (Prefect, MLflow, MinIO, Postgres)
- Run via `docker-compose up -d` before testing

**Integration Test Pattern:**
```python
import pytest
import subprocess

@pytest.fixture(scope="module")
def docker_services():
    """Ensure Docker services are running."""
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    yield
    # Teardown if needed

@pytest.fixture
def dvc_setup(docker_services):
    """Integration test fixture for DVC operations."""
    return DVCSetup(config_path="config/mlops_config.yaml")
```

## Coverage

**Requirements:** None currently enforced

**View Coverage:**
```bash
# If pytest-cov is installed
pytest --cov=src/nikhil/yantra --cov-report=html
```

**Recommended Target:** 80% coverage minimum

## Type Checking

**Tool:** `mypy` (referenced in README)

**Run Commands:**
```bash
mypy src/              # Type check all source
```

## Test Types

**Unit Tests:**
- Test individual classes and functions in isolation
- Mock external dependencies

**Integration Tests:**
- Test with actual infrastructure services
- May require Docker to be running

**E2E Tests:**
- Full workflow tests (e.g., DVC setup → sync → push)
- Requires all services running

## CI/CD

**Current State:** No CI/CD configuration detected

**Missing:**
- No GitHub Actions workflows (`.github/workflows/`)
- No GitLab CI configuration
- No CI pipeline for automated testing

**Recommended CI Pipeline:**
```yaml
# Example .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov mypy
      - name: Run tests
        run: pytest --cov=src
      - name: Type check
        run: mypy src/
```

## Test Command Reference

Based on README.md:

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
pytest

# Code formatting (before committing)
black src/

# Type checking
mypy src/
```

---

*Testing analysis: 2026-04-10*