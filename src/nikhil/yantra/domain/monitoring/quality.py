# src/nikhil/yantra/domain/monitoring/quality.py

import logging
import os
from typing import Optional

import nltk
import pandas as pd
from evidently import Report
from evidently.legacy.pipeline.column_mapping import ColumnMapping
from evidently.presets import TextEvals

from nikhil.yantra.domain.monitoring.model_monitor_protocol import IModelMonitor

logger = logging.getLogger(__name__)


class EvidentlyQualityMonitor(IModelMonitor):
    """
    A modern Evidently-based implementation of the IModelMonitor protocol.
    Provides text-quality evaluations (sentiment, length, OOV, etc.)
    for LLM-generated responses inside logs.
    """

    # Required NLTK resources for text analysis
    NLTK_REQUIREMENTS = [
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
        ("sentiment/vader_lexicon.zip", "vader_lexicon"),
        ("corpora/words", "words"),
    ]

    def __init__(self) -> None:
        self._ensure_nltk_resources()

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------
    def _download_if_missing(self, check_path: str, pkg_name: str) -> None:
        """Download an NLTK resource only if missing."""
        try:
            nltk.data.find(check_path)
        except LookupError:
            logger.info(f"Downloading missing NLTK resource: {pkg_name}")
            nltk.download(pkg_name, quiet=True)

    def _ensure_nltk_resources(self) -> None:
        """
        Ensures required NLTK corpora exist.
        Skips downloads if already cached (ideal for Docker or CI environments).
        """
        logger.debug("Checking required NLTK resources...")
        for check_path, pkg_name in self.NLTK_REQUIREMENTS:
            self._download_if_missing(check_path, pkg_name)
        logger.debug("NLTK resource validation complete.")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def generate_report(
        self,
        df_logs: pd.DataFrame,
        output_path: str = "quality_report.html",
        text_column: str = "response",
    ) -> str:
        """
        Generates an Evidently text-quality report and saves it as an HTML file.

        Args:
            df_logs: Pandas DataFrame with LLM logs.
            output_path: Path where the HTML report should be saved.
            text_column: Column containing LLM-generated text.

        Returns:
            Path to the saved HTML report.
        """
        logger.info(f"Generating Evidently Text Quality Report for '{text_column}'.")

        # Validation
        if text_column not in df_logs.columns:
            raise ValueError(
                f"Column '{text_column}' not found in DataFrame. "
                f"Available columns: {list(df_logs.columns)}"
            )

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Column mapping required by Evidently (modern API)
        column_mapping = ColumnMapping(
            task=None,
            text_features=[text_column],
        )

        # Configure report
        report = Report(metrics=[TextEvals()])

        try:
            report.run(
                current_data=df_logs,
                reference_data=None,  # No baseline; simple profiling run
            )

            report.save_html(output_path)

            logger.info(f"Quality Report successfully saved to: {output_path}")
            return output_path

        except Exception as exc:
            logger.error("Failed to generate Evidently report.", exc_info=True)
            raise RuntimeError(f"Evidently report generation failed: {exc}") from exc
