# Framework Dependencies - Status & Migration Roadmap

**Last Updated:** 2025-11-25  
**Review Schedule:** Quarterly (March, June, September, December)

---

## Purpose

This document tracks all external framework dependencies in Yantra, assesses their risks, and documents isolation strategies. As a common MLOps library, we must minimize framework coupling to ensure long-term stability.

---

## Critical Framework Dependencies

### 1. DVC-S3 (3.0.1)
**Category:** Data Versioning  
**Risk Level:** 🟡 **MEDIUM** - Infrastructure dependency

**Usage:**
- Data versioning in `domain/data_versioning/`
- S3/MinIO integration
- Git integration for `.dvc` files

**Isolation Status:** ⚠️ **Partial**
- Direct subprocess calls to `dvc` CLI
- Protocol defined (`IDataVersionControl`)
- Implementation via `DVCSetup` and `DVCDataTracker`

**Migration Path:**
1. Protocol already defined (`IDataVersionControl`)
2. Create `GitLFSVersioner` as alternative implementation
3. Create `LakeFSVersioner` for data lake scenarios
4. Update components to depend only on protocol

**Alternative Frameworks:**
- Git LFS (Large File Storage)
- LakeFS
- Pachyderm
- DeltaLake
- Custom S3 versioning

**Action Items:**
- [ ] Create Git LFS adapter (Q2 2026)
- [ ] Research LakeFS integration (Q3 2026)
- [x] Protocol defined and in use

---

### 2. MLflow (>= 2.10.0)
**Category:** Experiment Tracking  
**Risk Level:** 🟡 **MEDIUM** - Observability dependency

**Usage:**
- Experiment tracking in `domain/observability/`
- LLM trace logging
- Metric and parameter tracking

**Isolation Status:** ✅ **Good**
- Protocol defined (`IExperimentTracker`)
- `MLflowTracker` implements protocol
- Domain logic independent of MLflow specifics

**Migration Path:**
- Already well-isolated via protocol pattern
- Can add alternative implementations (Weights & Biases, Neptune, etc.)

**Alternative Frameworks:**
- Weights & Biases
- Neptune.ai
- Comet.ml
- Custom tracking backend

**Action Items:**
- ✅ Well isolated via protocol pattern
- [ ] Consider W&B adapter for teams already using it (Q4 2026)

---

### 3. Prefect (>= 2.14.0)
**Category:** Workflow Orchestration  
**Risk Level:** 🟡 **MEDIUM** - Orchestration dependency

**Usage:**
- Workflow orchestration in `domain/orchestration/`
- Task retry logic
- Custom `yantra_task` decorator

**Isolation Status:** ⚠️ **Partial**
- `yantra_task` decorator wraps Prefect's `@task`
- No protocol abstraction currently
- Direct dependency on Prefect decorators

**Migration Path:**
1. Create `ITaskOrchestrator` protocol
2. Create `PrefectOrchestrator` adapter
3. Create `AirflowOrchestrator` as alternative
4. Refactor `yantra_task` to use protocol

**Alternative Frameworks:**
- Apache Airflow
- Dagster
- Metaflow
- Flyte
- Custom orchestration

**Action Items:**
- [ ] Create `ITaskOrchestrator` protocol (Q1 2026)
- [ ] Implement Prefect adapter (Q2 2026)
- [ ] Add Airflow support for broader adoption (Q3 2026)

---

### 4. Evidently (>= 0.4.0)
**Category:** Model Monitoring  
**Risk Level:** 🟢 **LOW** - Isolated monitoring feature

**Usage:**
- Quality monitoring in `domain/monitoring/`
- Text evaluation metrics
- Report generation

**Isolation Status:** ✅ **Excellent**
- Used only in `QualityMonitor` class
- Simple wrapper around Evidently functionality
- Easy to swap with other monitoring tools

**Migration Path:**
- Already well-isolated
- Can add alternative monitoring implementations

**Alternative Frameworks:**
- WhyLabs
- Great Expectations
- DeepChecks
- Custom validation logic

**Action Items:**
- ✅ Well isolated, no action needed
- [ ] Consider Great Expectations integration (Optional, Q4 2026)

---

### 5. Boto3 (>= 1.34.0)
**Category:** Cloud Storage Client  
**Risk Level:** 🟢 **LOW** - Standard AWS SDK

**Usage:**
- S3/MinIO bucket management in `DVCSetup`
- Bucket creation and verification
- Storage backend configuration

**Isolation Status:** ✅ **Good**
- Used only in `DVCSetup._ensure_bucket_exists()`
- Minimal surface area
- Well-established library

**Migration Path:**
- Not needed - industry standard
- Could abstract behind storage protocol if needed

**Alternative Libraries:**
- MinIO SDK (for MinIO-only deployments)
- Google Cloud Storage client
- Azure Blob Storage client

**Action Items:**
- ✅ Well isolated, stable library
- [ ] Consider multi-cloud storage abstraction (Future)

---

## Utility Libraries (Low Risk)

These are stable, well-maintained libraries with minimal breaking change risk:

| Library | Version | Purpose | Risk | Isolation |
|---------|---------|---------|------|-----------|
| PyYAML | 6.0.2 | Config parsing | 🟢 LOW | ✅ Utils only |
| Pandas | (Optional) | Data processing | 🟢 LOW | ⚠️ Not currently used |

---

## Dependency Review Schedule

### Quarterly Review (Every 3 Months)

1. **Check for Updates:**
   ```bash
   pip list --outdated
   ```

2. **Review Changelogs:**
   - DVC: Check for CLI interface changes
   - MLflow: Review API updates
   - Prefect: Monitor decorator changes
   - Evidently: Check metric compatibility

3. **Update This Document:**
   - Change risk levels if frameworks become unmaintained
   - Update isolation status after refactoring
   - Document new dependencies

4. **Measure Coupling:**
   ```bash
   # Count direct framework imports in domain layer
   grep -r "import dvc" src/nikhil/yantra/domain/
   grep -r "import mlflow" src/nikhil/yantra/domain/
   grep -r "from prefect" src/nikhil/yantra/domain/
   ```

### Annual Review (Every 12 Months)

1. **Framework Health Assessment:**
   - Is the framework actively maintained?
   - Are there better alternatives?
   - What's the community size?

2. **Migration Feasibility:**
   - Cost/benefit of switching frameworks
   - Effort required for isolation
   - Impact on dependent projects

3. **Refactoring Priority:**
   - High-risk, poorly isolated → Immediate action
   - Medium-risk, partial isolation → Plan refactoring
   - Low-risk, well isolated → Monitor only

---

## Coupling Reduction Roadmap

### Q1 2026
- [ ] Create `ITaskOrchestrator` protocol for Prefect isolation
- [ ] Document workflow upgrade process
- [ ] Baseline coupling metrics

### Q2 2026
- [ ] Implement Prefect adapter using protocol
- [ ] Create Git LFS alternative for DVC
- [ ] Add W&B experiment tracker

### Q3 2026
- [ ] Add Airflow orchestration support
- [ ] Research LakeFS integration
- [ ] Measure coupling reduction

### Q4 2026
- [ ] Evaluate additional monitoring tools
- [ ] Complete Prefect isolation
- [ ] Reduce framework coupling to <5% in domain layer

---

## Framework Selection Criteria

When evaluating new framework dependencies, use these criteria:

### ✅ Prefer Frameworks That:
- Have active maintenance (commits in last 3 months)
- Have large community (>1000 GitHub stars)
- Follow semantic versioning
- Have clear upgrade paths
- Are abstraction-friendly (not tightly coupled)

### ❌ Avoid Frameworks That:
- Are abandoned (no commits in 6+ months)
- Have frequent breaking changes
- Lock you into specific infrastructure
- Are difficult to abstract/wrap
- Require global state

### 🔍 Evaluation Checklist:
- [ ] Check GitHub activity (commits, issues, PRs)
- [ ] Review changelog for breaking change frequency
- [ ] Test isolation (can we wrap it in an adapter?)
- [ ] Check for alternatives (are there better options?)
- [ ] Assess upgrade difficulty (major version migration path?)

---

## Emergency Response Plan

### If a Critical Framework is Deprecated:

1. **Assess Impact** (Week 1)
   - Identify all usage locations
   - Measure effort for migration
   - Check for viable alternatives

2. **Create Isolation Layer** (Weeks 2-4)
   - If not already isolated, create adapters
   - Define framework-agnostic protocols
   - Prevent further coupling

3. **Select Alternative** (Week 5)
   - Evaluate replacement frameworks
   - Create proof-of-concept
   - Test with real workloads

4. **Gradual Migration** (Weeks 6-12)
   - Implement new adapter
   - Add feature flag for switching
   - Test in non-production
   - Gradual rollout

5. **Deprecate Old** (Weeks 13-16)
   - Mark old adapter as deprecated
   - Update documentation
   - Remove after 1 minor version

---

## Metrics & Success Criteria

### Target Metrics:

| Metric | Current | Target (2026) |
|--------|---------|---------------|
| Domain layer framework imports | 5 | 0 |
| Framework coupling in domain | ~40% | 0% |
| Isolated frameworks (%) | 40% | 80% |
| Frameworks with protocols | 2 | 4 |
| Critical dependencies | 4 | 3 |

### Success Indicators:

✅ **Good Health:**
- All critical frameworks have protocol abstractions
- Domain layer has no direct framework imports
- Can swap major framework in <1 week
- Dependency updates don't break tests

⚠️ **Needs Attention:**
- Some domain code directly imports frameworks
- Framework upgrade requires code changes
- No clear migration path for critical dependency

🔴 **High Risk:**
- Business logic depends on framework-specific APIs
- Framework is unmaintained
- No alternative framework available
- Migration would require rewrite

---

**Next Review Date:** 2026-02-25  
**Responsible:** MLOps Team  
**Escalation:** If any dependency reaches 🔴 HIGH RISK, escalate immediately
