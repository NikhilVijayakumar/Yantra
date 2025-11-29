# src/nikhil/yantra/domain/orchestration/context.py
from typing import Optional

from yantra.domain.observability import IExperimentTracker


class YantraContext:
    """
    Singleton-style context to hold the active tracker.
    This avoids passing 'tracker' objects into every function.
    """
    _tracker: Optional[IExperimentTracker] = None

    @classmethod
    def set_tracker(cls, tracker: IExperimentTracker):
        cls._tracker = tracker

    @classmethod
    def get_tracker(cls) -> Optional[IExperimentTracker]:
        return cls._tracker