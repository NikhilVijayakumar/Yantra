"""Data versioning domain for DVC integration with S3/MinIO."""

from .dvc_setup import DVCSetup
from .dvc_tracker import DVCDataTracker
from .data_version_protocol import IDataVersionControl


def get_data_versioner(config_path: str) -> DVCDataTracker:
    """
    Factory function to get a data version tracker instance.
    
    Args:
        config_path: Path to YAML configuration file containing:
            - domain_root_path: Input data directory
            - output_dir_path: Output data directory
            - s3_config: S3/MinIO configuration
            - commit_message: Base message for git commits
        
    Returns:
        DVCDataTracker: Configured data version tracker
        
    Example:
        >>> tracker = get_data_versioner("config/app_config.yaml")
        >>> tracker.sync()  # Pull, validate, track, commit, push
    """
    return DVCDataTracker(config_path)


# Keep legacy import for backward compatibility
DVCDataTracker.__name__ = "DVCDataTracker"  # Ensure class name is preserved


__all__ = [
    'DVCSetup',
    'DVCDataTracker',
    'IDataVersionControl',
    'get_data_versioner'
]
