from abc import ABC, abstractmethod
from typing import Dict


class AIProvider(ABC):
    @abstractmethod
    async def summarize_report(self, content: str) -> Dict[str, str]:
        """Summarize a problem report and classify its type.

        Returns:
            dict with keys: summary (str), problem_type (str)
        """
        pass
