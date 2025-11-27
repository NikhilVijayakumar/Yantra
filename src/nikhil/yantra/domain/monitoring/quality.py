# src/nikhil/yantra/domain/monitoring/quality.py
import nltk
from typing import Optional
import pandas as pd

from evidently.report import Report
from evidently.metric_preset import TextEvals
from evidently.descriptors import Sentiment, TextLength
from evidently import ColumnMapping


class QualityMonitor:
    def __init__(self):
        # 1. Ensure NLTK data is available (run once)
        # This prevents "Resource not found" errors in production
        try:
            nltk.data.find('corpora/wordnet')
            nltk.data.find('corpora/omw-1.4')
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            print("📦 Downloading necessary NLTK data for text evaluation...")
            nltk.download('words', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            nltk.download('vader_lexicon', quiet=True)

    def generate_report(self,
                        df_logs: pd.DataFrame,
                        output_path: str = "quality_report.html",
                        text_column: str = "response") -> str:
        """
        Generates an HTML report for LLM text quality.

        Args:
            df_logs: DataFrame containing the text logs.
            output_path: Where to save the HTML report.
            text_column: Name of the column containing the LLM response.
        """
        # 2. Define Column Mapping
        # Critical: Tell Evidently which column holds the text data!
        column_mapping = ColumnMapping(
            text_features=[text_column]  # Treat 'response' as text, not categorical
        )

        # 3. Define the Report
        report = Report(metrics=[
            TextEvals(column_name=text_column, descriptors=[
                Sentiment(),  # VADER-based sentiment (Pos/Neg/Neu)
                TextLength()  # Character/Word count stats
            ])
        ])

        print(f"📊 Generating quality report for {len(df_logs)} records...")

        # 4. Run with Mapping
        report.run(
            reference_data=None,
            current_data=df_logs,
            column_mapping=column_mapping
        )

        report.save_html(output_path)
        print(f"✅ Report saved to: {output_path}")
        return output_path