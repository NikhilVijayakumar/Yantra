# External Integrations

**Analysis Date:** 2026-04-10

## APIs & External Services

**MLOps Platforms:**
- MLflow - Experiment tracking server
  - Implementation: `mlflow` Python SDK
  - Connection: `MLFLOW_TRACKING_URI` env var or direct URL
  - Used in: `src/nikhil/yantra/domain/observability/mlflow_tracker.py`

- Prefect - Workflow orchestration
  - Implementation: `prefect` Python SDK (`prefect.task` decorator)
  - Connection: `PREFECT_API_URL` env var
  - Used in: `src/nikhil/yantra/domain/orchestration/prefect_utils.py`

- DVC - Data versioning
  - Implementation: `dvc-s3` Python package + CLI
  - Connection: S3/MinIO backend via `boto3`
  - Used in: `src/nikhil/yantra/domain/data_versioning/`

**LLM Services (Optional):**
- Google Gemini - LLM processing
  - SDK: `google-genai` (not in dependencies, documented in README)
  - Auth: `GEMINI_API_KEY` environment variable
  - Configuration: `config/mlops_config.yaml` (gemini_config section)

## Data Storage

**Object Storage:**
- MinIO (local S3-compatible)
  - Connection: `http://localhost:9000` or custom endpoint
  - Client: `boto3` with `botocore`
  - Authentication: Access key ID / Secret access key
  - Buckets: `mlflow-bucket`, `prefect-bucket` (auto-created), `yantra-data` (user-configurable)

- AWS S3 (production option)
  - Same `boto3` client interface
  - Configured via: `s3_config` in YAML or environment

**Databases:**
- PostgreSQL 15
  - Connection: `postgresql://postgres:password@postgres:5432/<db_name>`
  - Default databases: `mlflow_db`, `prefect_db`
  - Client: `psycopg2-binary` (installed in MLflow container)
  - Used by: MLflow backend store, Prefect API database

**File Storage:**
- Local filesystem for data input/output
  - Configured via: `domain_root_path`, `output_dir_path` in YAML config
  - Versioned data stored in DVC remote (MinIO/S3)

**Caching:**
- None detected

## Authentication & Identity

**API Keys:**
- `GEMINI_API_KEY` - Google Gemini (optional)
- MinIO credentials: `MINIO_ROOT_USER`/`MINIO_ROOT_PASSWORD` (default: minioadmin)

**AWS Credentials:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_ENDPOINT_URL` (for MinIO)

**Database Credentials:**
- PostgreSQL: `POSTGRES_USER`/`POSTGRES_PASSWORD` (default: postgres/password)

**Environment Configuration:**
- `python-dotenv` loads `.env` files
- All credentials documented in README

## MLflow Integration Details

**Tracking Server:**
- URI: `http://localhost:5000` (default)
- Backend: PostgreSQL (`mlflow_db`)
- Artifacts: MinIO S3 bucket (`mlflow-bucket`)
- SDK: `mlflow` Python package

**Key Features Used:**
- `mlflow.start_run()` - Run management
- `mlflow.log_param()` / `mlflow.log_metric()` - Logging
- `mlflow.log_artifact()` - File artifacts
- `mlflow.metrics.genai` - LLM evaluation metrics

## Prefect Integration Details

**Server:**
- URL: `http://localhost:4200` (default)
- Database: PostgreSQL (`prefect_db`)
- Blocks storage: MinIO/S3

**Key Features Used:**
- `@prefect.task` decorator (via `yantra_task` wrapper)
- `prefect.get_run_logger()` - Logging integration
- Retry logic support

## DVC Integration Details

**Remote Storage:**
- Type: S3 (MinIO or AWS)
- Client: `boto3` with custom endpoint URL
- Configuration: `s3_config` in YAML

**Key Features Used:**
- DVC CLI commands via subprocess
- `dvc pull` / `dvc push` - Data sync
- S3 bucket management via boto3

## Evidently Integration Details

**Monitoring:**
- Type: Python library (not a service)
- Client: `evidently` package
- Used in: `src/nikhil/yantra/domain/monitoring/quality.py`

**Key Features Used:**
- `evidently.Report` - Quality reports
- `evidently.presets.TextEvals` - Text evaluation
- NLTK integration for text metrics

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/Bugsnag)

**Logs:**
- Prefect logger (`prefect.get_run_logger()`)
- Python standard logging

**Metrics:**
- MLflow for experiment metrics
- Evidently for data/model quality metrics

## CI/CD & Deployment

**Hosting:**
- Self-hosted via Docker Compose
- No cloud托管platform detected

**CI Pipeline:**
- None detected in repository

## Environment Configuration

**Required env vars (docker-compose):**
- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`
- `POSTGRES_USER` / `POSTGRES_PASSWORD`
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `MLFLOW_BACKEND_STORE_URI`
- `PREFECT_API_DATABASE_CONNECTION_URL`

**Optional env vars:**
- `GEMINI_API_KEY` - For LLM features

**Secrets location:**
- `.env` file (gitignored, loaded via python-dotenv)
- Docker Compose environment section

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- DVC remote push to S3/MinIO
- Prefect webhook blocks (optional, documented)

---

*Integration audit: 2026-04-10*