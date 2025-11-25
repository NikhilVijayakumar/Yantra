# src/nikhil/yantra/domain/monitoring/quality.py
from evidently.report import Report
from evidently.metric_preset import TextEvals
from evidently.descriptors import Sentiment, TextLength


class QualityMonitor:
    def generate_report(self, df_logs, output_path="report.html"):
        # Create a report for LLM text quality
        report = Report(metrics=[
            TextEvals(column_name="response", descriptors=[
                Sentiment(),
                TextLength()
            ])
        ])

        report.run(reference_data=None, current_data=df_logs)
        report.save_html(output_path)
        return output_path