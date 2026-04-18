# Project: Yantra

**Type:** MLOps Library  
**Core Value:** Unified MLOps for AI agents - one library replaces DVC, MLflow, Prefect, Evidently  
**Last updated:** 2026-04-10 after initialization

## What This Is

Yantra is a standalone MLOps library that wraps Essential MLOps tools (DVC, MLflow, Prefect, Evidently) into a unified, protocol-based interface. Users wrap Yantra only - no need to use individual tools directly. Designed for agentic AI systems and research purposes.

## Context

**Brownfield:** Existing code in project with protocol-based architecture already implemented.

### Existing Capabilities (Validated)

- ✓ DVC-based data versioning with S3 remote
- ✓ MLflow experiment tracking with LLM tracing
- ✓ Prefect task orchestration with dual-purpose decorator
- ✓ Evidently quality monitoring for text data
- ✓ ModelArena for LLM comparison
- ✓ YantraContext singleton for global tracker management

### Architecture

Protocol-based dependency inversion:
- Protocol Layer: `IDataVersionControl`, `IExperimentTracker`, `IModelMonitor`
- Domain Layer: Concrete implementations (DVCDataTracker, MLflowTracker, EvidentlyQualityMonitor)
- Orchestration Layer: `@yantra_task` decorator combining Prefect + MLflow

### Stack

- Python 3.12+
- DVC 3.x, MLflow 3.x, Prefect 3.x, Evidently 0.7.x
- S3 for remote storage
- Configuration via YAML files

## Users

**Primary:** AI Researchers AND Agent Developers

Both building MLOps research papers and building AI agents that need MLOps capabilities.

## Goal for This Phase

Polish existing implementation and publish high-quality research paper.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Protocol-based design | Swappable implementations, research flexibility | — Pending |
| Unified wrapper | Simpler for agents, single interface | — Pending |
| Research + paper focus | Validate architecture through publishing | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state