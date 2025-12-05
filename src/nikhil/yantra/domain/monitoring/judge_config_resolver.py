from typing import Optional, Dict, Any


class SimpleJudgeConfigResolver:
    """A lightweight resolver that returns judge rules based on a provided
    mapping or a default rule set. Clients should implement a resolver for
    production to map platform-specific constraints.
    """


    def __init__(self, mapping: Optional[Dict[str, Dict[str, Any]]] = None, default: Optional[Dict[str, Any]] = None):
        self.mapping = mapping or {}
        self.default = default or {"scoring_method": "scaled", "weights": {"coherence": 0.6, "safety": 0.4}}


    def get_rules(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # context can contain 'platform' or 'columns' or any metadata
        platform = context.get("platform")
        if platform and platform in self.mapping:
            return self.mapping[platform]
        return self.default