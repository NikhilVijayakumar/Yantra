import json

import requests

class LMStudioClient:
    """LM Studio client that hits a local OpenAI-compat endpoint.


    Expects LM Studio running with an OpenAI-compatible endpoint like:
    http://localhost:1234/v1/chat/completions
    """


    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1/chat/completions", model: str = "gpt-oss-20b"):

        self.requests = requests
        self.base_url = base_url
        self.model = model


    def generate(self, prompt: str, **kwargs) -> str:
        payload = {
        "model": self.model,
        "messages": [{"role": "user", "content": prompt}],
        **kwargs,
        }
        r = self.requests.post(self.base_url, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        # Compatible with many OpenAI-style responses
        try:
            return j["choices"][0]["message"]["content"]
        except Exception:
            return json.dumps(j)