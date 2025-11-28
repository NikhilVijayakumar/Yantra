# Yantra

**Yantra** is a unified MLOps library that provides clean, protocol-based interfaces for essential MLOps tools including DVC, MLflow, Prefect, and Evidently.

## 🎯 Purpose

Yantra simplifies MLOps workflows by providing:
- **Data Versioning** with DVC and S3/MinIO
- **Experiment Tracking** with MLflow
- **Workflow Orchestration** with Prefect
- **Model Monitoring** with Evidently

## 🚀 Features

### Data Versioning (`nikhil.yantra.domain.data_versioning`)
- **DVCSetup**: Automated DVC initialization with S3/MinIO backend
- **DVCDataTracker**: Collaborative data syncing workflow (pull → validate → track → push)
- **Protocol-based design** via `IDataVersionControl`

### Experiment Tracking (`nikhil.yantra.domain.observability`)
- **MLflowTracker**: Experiment tracking with MLflow integration
- **ModelArena**: Comparison framework for LLMs using MLflow Evaluate
- **Protocol-based design** via `IExperimentTracker`
- LLM trace logging support

### Workflow Orchestration (`nikhil.yantra.domain.orchestration`)
- **yantra_task**: Custom Prefect decorator with auto-logging
- Retry logic and task monitoring

### Model Monitoring (`nikhil.yantra.domain.monitoring`)
- **EvidentlyQualityMonitor**: Generate quality reports using Evidently
- **Protocol-based design** via `IModelMonitor`
- Text evaluation metrics (sentiment, length, etc.)

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Git
- Docker & Docker Compose (running)

### Infrastructure Services

Ensure the following services are running via `docker-compose up -d` before starting:

| Service | URL | Description | Credentials |
| :--- | :--- | :--- | :--- |
| **Prefect UI** | [http://localhost:4200](http://localhost:4200) | Workflow Orchestration | None |
| **MLflow UI** | [http://localhost:5000](http://localhost:5000) | Experiment Tracking | None |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | S3 Storage UI | `minioadmin` / `minioadmin` |
| **MinIO API** | `http://localhost:9000` | S3 API Endpoint | `minioadmin` / `minioadmin` |
| **Postgres** | `localhost:5432` | Database | `postgres` / `password` |

> [!IMPORTANT]
> **Always use a virtual environment!**
> 
> Never install this package globally. Always create and activate a virtual environment before installation to avoid conflicts with system packages and ensure isolated dependencies.

### Installation Steps

```bash
# Clone the repository
git clone <your-repo-url>
cd Yantra

# Create virtual environment
python -m venv venv

# Activate virtual environment (REQUIRED!)
source venv/bin/activate  # On Linux/Mac
# or
.\\venv\\Scripts\\Activate.ps1  # On Windows PowerShell

# Verify virtual environment is active
# You should see (venv) in your terminal prompt

# Install in editable mode
pip install -e .
```

## 🏃 Quick Start

### Data Versioning with DVC

```python
from nikhil.yantra.domain.data_versioning import DVCSetup, DVCDataTracker

# Initial setup (run once)
setup = DVCSetup(config_path="config/mlops_config.yaml")
setup.setup()

# Ongoing data management
tracker = DVCDataTracker(config_path="config/mlops_config.yaml")
tracker.sync()  # Pull → Validate → Track → Push
```

### Experiment Tracking with MLflow

```python
from nikhil.yantra.domain.observability import MLflowTracker

# Initialize tracker
tracker = MLflowTracker(
    tracking_uri="http://localhost:5000",
    experiment_name="my_experiment"
)

# Log experiments
tracker.log_llm_trace(
    name="Chat Completion",
    inputs={"prompt": "What is MLOps?"},
    outputs={"response": "MLOps is..."},
    metadata={"model_name": "gpt-4"}
)
```

### Workflow Orchestration with Prefect

```python
from nikhil.yantra.domain.orchestration import yantra_task

@yantra_task(retries=3)
def process_data(data_path: str):
    # Your data processing logic
    return processed_data
```

### Model Monitoring with Evidently

```python
from nikhil.yantra.domain.monitoring import EvidentlyQualityMonitor
import pandas as pd

monitor = EvidentlyQualityMonitor()
df_logs = pd.DataFrame({
    "response": ["Great product!", "Terrible experience"]
})

report_path = monitor.generate_report(df_logs, output_path="quality_report.html")
```

### Gemini Production Flow Example

A complete production-ready example using Gemini, DVC, MLflow, and Prefect is available in `src/nikhil/yantra/example/production_flow.py`.

**Prerequisites:**
- Set `GEMINI_API_KEY` in your `.env` file.
- Ensure `google-genai` is installed.

**Running the Flow:**
```bash
python src/nikhil/yantra/example/production_flow.py
```

This flow will:
1. Ingest and version data using DVC.
2. Process data using Gemini (traced by MLflow).
3. Monitor quality using Evidently and version the report.

## 📋 Configuration

Create a YAML configuration file (e.g., `mlops_config.yaml`):

```yaml
# Data paths
domain_root_path: ./data/input
output_dir_path: ./data/output

# DVC commit message
commit_message: "Data update"

# S3/MinIO configuration
s3_config:
  bucket_name: "yantra-data"
  endpoint_url: "http://localhost:9000"
  access_key_id: "minioadmin"
  secret_access_key: "minioadmin"
  region: "us-east-1"
  use_ssl: false
```

## 🏗️ Architecture

Yantra follows **Clean Architecture** principles with clear separation of concerns:

```
src/nikhil/yantra/
├── domain/              # Core business logic
│   ├── data_versioning/ # DVC integration
│   ├── observability/   # MLflow integration
│   ├── orchestration/   # Prefect integration
│   └── monitoring/      # Evidently integration
└── utils/               # Shared utilities
```

### Design Principles

- **Protocol-based interfaces**: External boundaries use `Protocol` for duck typing
- **Dependency injection**: Components receive dependencies via constructor
- **Configuration-driven**: Behavior controlled via YAML configuration
- **Framework isolation**: Business logic independent of specific tool implementations

See [docs/Architecture.md](docs/Architecture.md) for detailed architectural guidelines.

## 📚 Documentation

- [Architecture Guide](docs/Architecture.md) - Coding standards and design patterns
- [Dependencies](docs/DEPENDENCIES.md) - Framework dependencies and isolation strategies
- [Virtual Environment Usage](docs/VIRTUAL_ENV_USAGE.md) - Development environment setup

## 🔧 Development

> [!NOTE]
> **Always activate your virtual environment before development work!**
> 
> See [Virtual Environment Usage Guide](docs/VIRTUAL_ENV_USAGE.md) for detailed instructions and troubleshooting.

```bash
# Activate virtual environment first!
source venv/bin/activate  # On Linux/Mac
# or
.\\venv\\Scripts\\Activate.ps1  # On Windows PowerShell

# Verify activation (should show venv path)
echo $VIRTUAL_ENV  # Linux/Mac
# or
$env:VIRTUAL_ENV  # Windows PowerShell

# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
pytest

# Code formatting
black src/

# Type checking
mypy src/
```

## 🌟 Key Components

| Component | Purpose | Protocol |
|-----------|---------|----------|
| `DVCSetup` | Initialize DVC with S3 | `IDataVersionControl` |
| `DVCDataTracker` | Sync data versions | `IDataVersionControl` |
| `MLflowTracker` | Track experiments | `IExperimentTracker` |
| `ModelArena` | Compare LLM performance | N/A |
| `yantra_task` | Orchestrate workflows | N/A (decorator) |
| `EvidentlyQualityMonitor` | Monitor model quality | `IModelMonitor` |

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📞 Support

[Add support information here]
