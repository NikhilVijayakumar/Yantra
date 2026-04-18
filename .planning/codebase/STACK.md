# Technology Stack

**Analysis Date:** 2026-04-10

## Languages

**Primary:**
- Python 3.8+ - Core language (per README requirement)

**Secondary:**
- None detected

## Runtime

**Environment:**
- Standard Python runtime
- Virtual environment required (see README documentation)

**Package Manager:**
- pip (with pyproject.toml)
- No lockfile detected

## Frameworks

**Core MLOps Frameworks:**
- `dvc-s3` 3.0.1 - Data Version Control with S3 backend
- `mlflow` 3.6.0 - Experiment tracking
- `prefect` 3.6.4 - Workflow orchestration
- `evidently` 0.7.17 - Model monitoring

**Data Processing:**
- `pandas` 2.3.2 - Data manipulation
- `numpy` 2.2.6 - Numerical computing

**NLP:**
- `nltk` 3.9.2 - Natural language processing

**Cloud/Storage:**
- `boto3` 1.34.0 - AWS SDK for Python

**Configuration:**
- `PyYAML` 6.0.3 - YAML configuration parsing
- `python-dotenv` 1.2.1 - Environment variable loading

**Development Tools:**
- `watchfiles` 1.1.1 - File watching for development

## Key Dependencies

**MLOps Core:**
- `Nibandha[export]` - Local dependency (file:// URL), custom framework
- `dvc-s3` 3.0.1 - DVC configured for S3/MinIO storage
- `mlflow` 3.6.0 - Experiment tracking server
- `prefect` 3.6.4 - Workflow orchestration engine
- `evidently` 0.7.17 - Model quality monitoring

**Infrastructure:**
- `boto3` 1.34.0 - S3/MinIO connectivity
- `pandas` 2.3.2 - Data handling
- `PyYAML` 6.0.3 - Configuration files

**Testing:**
- Not detected in dependencies (pytest mentioned in README but not in pyproject.toml)

**Build:**
- setuptools (via `[tool.setuptools]` in pyproject.toml)
- Package location: `src/nikhil` (custom package-dir mapping)

## Configuration

**Environment:**
- `.env` files supported via `python-dotenv`
- YAML configuration files (e.g., `config/mlops_config.yaml`)
- Typical env vars: `GEMINI_API_KEY`, AWS credentials, database connection strings

**Build:**
- `pyproject.toml` - Modern Python package configuration
- Package structure: Single namespace `nikhil` mapped to `src/nikhil`

**Project Structure:**
```
Yantra/
├── src/nikhil/yantra/     # Main package
├── config/                # Configuration YAML files
├── docker-compose.yml      # Infrastructure services
└── docs/                  # Documentation
```

## Platform Requirements

**Development:**
- Python 3.8 or higher
- Git
- Docker & Docker Compose (for infrastructure services)
- Virtual environment required

**Production:**
- Python runtime
- Running infrastructure (MinIO, PostgreSQL, MLflow, Prefect)
- S3-compatible storage (MinIO or AWS S3)

## Docker Infrastructure Services

**Provided via docker-compose.yml:**
- MinIO (S3 storage) - Port 9000/9001
- PostgreSQL 15 - Port 5432
- MLflow v3.6.0 - Port 5000
- Prefect v3 (latest) - Port 4200

**Notable Absence:**
- No dedicated Evidently service (runs as Python library)
- No Redis/caching service

---

*Stack analysis: 2026-04-10*