# src/nikhil/yantra/domain/monitoring/interfaces.py
from typing import Protocol, runtime_checkable, Optional
import pandas as pd


@runtime_checkable
class IModelMonitor(Protocol):
    """
    Protocol for Model Monitoring systems.
    Allows swapping implementations (e.g., Evidently, DeepChecks, Whylogs).
    """

    def generate_report(self,
                        df_logs: pd.DataFrame,
                        output_path: str,
                        text_column: str = "response") -> str:
        """
        Generates a quality report from log data.

        Args:
            df_logs: The dataframe containing model inputs/outputs.
            output_path: File path where the report (HTML/JSON) will be saved.
            text_column: The specific column name to analyze for text metrics.

        Returns:
            str: The path to the generated report.
        """
        ...