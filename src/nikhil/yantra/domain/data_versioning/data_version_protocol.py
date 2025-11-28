# src/nikhil/yantra/domain/data_versioning/data_version_protocol.py
from typing import Protocol, runtime_checkable
from pathlib import Path


@runtime_checkable
class IDataVersionControl(Protocol):
    """Protocol for data versioning systems."""

    def setup(self) -> None:
        """Initialize the DVC environment."""
        ...

    def track(self, path: Path = None) -> None:
        """Add data to version control."""
        ...

    def pull(self) -> None:
        """Fetch latest data from remote."""
        ...

    def push(self) -> None:
        """Upload local data to remote."""
        ...

    def sync(self) -> None:
        """Execute full sync workflow (Pull -> Track -> Push)."""
        ...