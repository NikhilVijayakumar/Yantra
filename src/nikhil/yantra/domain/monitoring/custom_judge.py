import json
import logging
import re
from typing import Dict, Any, Optional, List
from yantra.domain.monitoring.llm_client_protocol import ILlmClient
from yantra.domain.monitoring.model_judge_protocol import IModelJudge

logger = logging.getLogger(__name__)

class CustomMetricLlmJudge(IModelJudge):
    DEFAULT_TEMPLATE = (
        "You are an impartial evaluation judge.\n"
        "Your task is to evaluate the following input based on the provided metrics configuration.\n\n"
        "### Input to Evaluate:\n"
        "{prompt}\n\n"
        "### Metrics Configuration:\n"
        "{rules}\n\n"
        "### Instructions:\n"
        "1. Analyze the input against each metric defined in the configuration.\n"
        "2. Provide a score and a rationale for each metric.\n"
        "3. Your output MUST be a valid JSON object matching the expected structure.\n"
        "4. The output must contain an 'evaluation' key which is a list of objects, each containing 'metricName', 'score', and 'rationale'.\n"
        "5. Do NOT include any markdown formatting (like ```json ... ```) in your response, just the raw JSON string.\n"
        "\n"
        "### Output JSON:\n"
    )

    def __init__(self, llm_client: ILlmClient, prompt_template: Optional[str] = None):
        self.llm_client = llm_client
        self.prompt_template = prompt_template or self.DEFAULT_TEMPLATE

    def _extract_json(self, text: str) -> str:
        """Finds the largest substring that looks like a JSON object."""
        try:
            # Look for the first outer curly brace and the last outer curly brace
            # We strip code fences if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return match.group(1)
            return text
        except Exception:
            return text

    def judge(self, prompt: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the prompt using the given rules (metrics configuration).
        Returns a FLATTENED dictionary suitable for Evidently.
        """
        # 1. Construct the prompt
        meta_prompt = self.prompt_template.format(
            rules=json.dumps(rules, indent=2),
            prompt=prompt
        )

        # 2. Call LLM
        raw_output = self.llm_client.generate(meta_prompt)
        # logger.debug(f"Raw LLM Output: {raw_output}")

        # 3. Clean and Parse JSON
        clean_output = self._extract_json(raw_output)
        
        flat_result = {}
        
        try:
            parsed_json = json.loads(clean_output)
            
            # The user expects: { "arc_title_evaluated": "...", "evaluation": [ ... ] }
            # We want to flatten "evaluation" items.
            
            # Preserve top-level keys that are simple values
            for k, v in parsed_json.items():
                if isinstance(v, (str, int, float, bool)):
                    flat_result[k] = v
            
            # Flatten 'evaluation' list
            evaluations = parsed_json.get("evaluation", [])
            if isinstance(evaluations, list):
                for item in evaluations:
                    metric_name = item.get("metricName")
                    score = item.get("score")
                    rationale = item.get("rationale")
                    
                    if metric_name:
                        # Clean metric name for use as a column key (optional, but good practice)
                        # But Evidently can handle spaces. Let's keep it simple.
                        flat_result[f"{metric_name}_score"] = score
                        flat_result[f"{metric_name}_rationale"] = rationale
            
            # Fallback if structure is different but still contains useful info? 
            # For now, stick to the contract.
            
            flat_result["raw_llm_json"] = clean_output # Store raw json for debugging if needed (might be too large)
            
            return flat_result

        except json.JSONDecodeError:
            logger.error(f"JSON Parse Error. Raw: {raw_output}")
            return {
                "error": "Failed to parse Judge output",
                "raw_output": raw_output
            }
