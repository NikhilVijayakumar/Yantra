"""Protocol for data versioning systems."""

from typing import Protocol, Optional
from pathlib import Path


class IDataVersionControl(Protocol):
    """
    Protocol for data versioning systems (DVC, LakeFS, DagsHub, etc.).
    
    Defines the interface for tracking, syncing, and versioning datasets
    across different storage backends.
    """
    
    def setup(self) -> None:
        """
        Initialize the data versioning system.
        
        This includes configuring remote storage, creating necessary
        directories, and setting up tracking metadata.
        """
        ...
    
    def track(self, path: Path) -> None:
        """
        Add a file or directory to version control.
        
        Args:
            path: Path to file or directory to track
        """
        ...
    
    def pull(self) -> None:
        """
        Pull latest data from remote storage.
        
        Downloads the most recent version of tracked data from
        the configured remote storage backend.
        """
        ...
    
    def push(self) -> None:
        """
        Push local data to remote storage.
        
        Uploads local changes to the configured remote storage backend.
        """
        ...
    
    def sync(self) -> None:
        """
        Full synchronization workflow.
        
        Typically includes: pull latest changes, validate data,
        track new changes, commit metadata, and push to remote.
        """
        ...
