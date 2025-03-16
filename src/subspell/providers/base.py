from abc import ABC, abstractmethod


class ModelProvider(ABC):
    """Base class for all model providers."""

    @abstractmethod
    def correct_text(self, text: str) -> str:
        """
        Correct spelling, punctuation and grammar in text.

        Args:
            text: The text to correct

        Returns:
            The corrected text
        """
        pass
