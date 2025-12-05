import json
import logging
from typing import Optional, Any, Dict

from google import genai
from google.genai import types

# Assuming ILlmClient is imported from your protocol file
# from yantra.domain.monitoring.llm_client_protocol import ILlmClient

logger = logging.getLogger(__name__)


class GeminiClient:  # strictly implements ILlmClient
    """
    Robust Gemini client implementation using google-genai SDK (v1.0+).
    """

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", **genai_kwargs):
        """
        Args:
            api_key: Google GenAI API key.
            model: Model ID (e.g., 'gemini-2.0-flash').
            **genai_kwargs: Default generation parameters (e.g., temperature=0.7).
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model

        # Default safety: Block nothing to allow judge/evaluation tasks
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]

        self.default_genai_kwargs = genai_kwargs

    def _extract_text(self, response) -> str:
        """Safe extraction handling blocked content or API artifacts."""
        try:
            # 1. Check if the model refused to answer (Safety)
            if response.candidates:
                first_candidate = response.candidates[0]
                if first_candidate.finish_reason == "SAFETY":
                    logger.warning(f"Response blocked. Reason: {first_candidate.finish_reason}")
                    return json.dumps({
                        "score": 0.0,
                        "explanation": f"Blocked by Safety Filter ({first_candidate.finish_reason})"
                    })

            # 2. Attempt to return text
            if response.text:
                return response.text

            return ""

        except ValueError:
            # response.text raises ValueError if content is empty/blocked
            return json.dumps({"score": 0.0, "explanation": "Empty/Blocked Response"})
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates a response for the given prompt, adhering to ILlmClient.

        Maps 'prompt' -> SDK 'contents'
        Maps 'kwargs' -> SDK 'config'
        """
        # Merge default kwargs (from init) with request-specific kwargs
        # Request kwargs take precedence
        merged_params = {**self.default_genai_kwargs, **kwargs}

        # Construct the configuration object required by the new SDK
        # We explicitly set safety settings here to ensure consistency
        config = types.GenerateContentConfig(
            safety_settings=self.safety_settings,
            **merged_params
        )

        try:
            # Call the SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,  # PROTOCOL (prompt) -> SDK (contents)
                config=config
            )

            # Return string as required by ILlmClient -> str
            return self._extract_text(response)

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Return a JSON string so downstream JSON parsers (if any) handle it gracefully
            return json.dumps({"score": 0.0, "explanation": f"API Error: {str(e)}"})