from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path


class ModelProvider(ABC):
    """Base class for all model providers."""

    def __init__(
        self,
        system_instruction: Optional[str] = None,
        system_instruction_file: Optional[str] = None,
        temperature: float = 0.2,
        top_k: int = 40,
        top_p: float = 0.95,
    ):
        """
        Initialize the provider with optional system instructions and generation parameters.

        Args:
            system_instruction: Inline system instruction text
            system_instruction_file: Path to a file containing system instructions
            temperature: Controls randomness in the output (0.0 to 1.0)
            top_k: Controls diversity via top-k sampling
            top_p: Controls diversity via nucleus sampling
        """
        self.system_instruction = system_instruction
        self.system_instruction_file = system_instruction_file
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p

    def _load_system_instruction(self) -> Optional[str]:
        """
        Load system instruction from file or return inline instruction.

        Returns:
            The system instruction text, or None if not set
        """
        if self.system_instruction:
            return self.system_instruction
        
        if self.system_instruction_file:
            try:
                file_path = Path(self.system_instruction_file)
                if not file_path.exists():
                    raise FileNotFoundError(f"System instruction file not found: {file_path}")
                return file_path.read_text(encoding='utf-8')
            except Exception as e:
                raise ValueError(f"Failed to load system instruction file: {str(e)}")
        
        return None

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
