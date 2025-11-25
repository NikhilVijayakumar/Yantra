"""YAML utility functions for configuration file loading."""

import yaml
from pathlib import Path
from typing import Any, Dict, Union


class YamlUtils:
    """
    Utility class for YAML configuration file operations.
    
    Provides safe loading of YAML files with proper error handling.
    """
    
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
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"YAML configuration file not found: {path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config if config is not None else {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {path}: {e}")
    
    @staticmethod
    def yaml_safe_dump(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
        """
        Safely write data to a YAML configuration file.
        
        Args:
            data: Dictionary to write to YAML
            file_path: Path where the YAML file should be written
            
        Raises:
            yaml.YAMLError: If the data cannot be serialized to YAML
        """
        path = Path(file_path)
        
        try:
            with open(path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error writing YAML file {path}: {e}")
