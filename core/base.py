from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

class BaseDetector(ABC):
    """
    Base class for all forensic detectors in IH-Korupsi.
    Every detector must provide a deterministic mathematical explanation for its flags.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the detector."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of the detector's logic."""
        pass

    @abstractmethod
    def run(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Execute the detection logic on the provided DataFrame.
        Returns a dictionary containing findings, statistics, and flagged records.
        """
        pass

    def explain(self, finding_id: str) -> str:
        """
        Provide a mathematical explanation for a specific finding.
        Can be overridden for complex logic.
        """
        return f"Finding {finding_id} was flagged based on the {self.name} algorithm rules."
