import os
import logging
import json
import traceback
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types

from .base import ModelProvider
from ..language_rules import BG_SYSTEM_INSTRUCTION

logger = logging.getLogger("subspell-gemini")

class GeminiProvider(ModelProvider):
    """Gemini API provider for spell checking."""

    def __init__(
        self,
        api_key: str,
        system_instruction: Optional[str] = None,
        system_instruction_file: Optional[str] = None,
        temperature: float = 0.2,
        top_k: int = 40,
        top_p: float = 0.95,
        model: str = "gemini-2.0-flash",
    ):
        """
        Initialize the Gemini provider.

        Args:
            api_key: Gemini API key
            system_instruction: Inline system instruction text
            system_instruction_file: Path to a file containing system instructions
            temperature: Controls randomness in the output (0.0 to 1.0)
            top_k: Controls diversity via top-k sampling
            top_p: Controls diversity via nucleus sampling
            model: The Gemini model to use (e.g. "gemini-2.0-flash", "gemini-2.0-flash-experimental")
        """
        super().__init__(
            system_instruction=system_instruction,
            system_instruction_file=system_instruction_file,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
        )
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def _get_system_instruction(self) -> List[types.Part]:
        """Get the system instruction for the model."""
        # Try to load custom instruction
        custom_instruction = self._load_system_instruction()
        if custom_instruction:
            logger.info("Using custom system instruction")
            return [types.Part.from_text(text=custom_instruction)]

        # Fall back to default instruction
        logger.info("Using default system instruction")
        return [types.Part.from_text(text=BG_SYSTEM_INSTRUCTION)]

    def _get_example_content(self) -> List[types.Content]:
        """Get example content for the model."""
        return [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="""Какво ще правябрат ми жена не ме е остъвила.
Тя е перфектна, брат ми.
Човека щеме смаше пот обувкитеси, немога да му кажа нишо."""
                    ),
                ],
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(
                        text="""Какво ще правя? Брат ми жена не ме е оставила.
Тя е перфектна, брат ми.
Човекът ще ме смаже под обувките си, не мога да му кажа нищо.
"""
                    ),
                ],
            ),
        ]

    def correct_text(self, text: str) -> str:
        """
        Correct spelling, punctuation and grammar in text using Gemini.

        Args:
            text: The text to correct

        Returns:
            The corrected text
        """
        logger.info("Preparing to correct text")

        # Check if text is empty
        if not text or not text.strip():
            logger.warning("Empty text provided to correct_text()")
            return text

        # Add logging to verify input integrity
        logger.info(f"Text length received by provider: {len(text)} characters")
        import hashlib

        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        logger.info(f"Text hash in provider: {text_hash}")

        # Log input text boundaries for verification
        if len(text) > 200:
            logger.info(f"Text start: {text[:100]}...")
            logger.info(f"Text end: ...{text[-100:]}")

        # Save full input to a debug file
        try:
            from datetime import datetime
            from pathlib import Path
            import os

            dumps_dir = Path(os.path.expanduser("~/subspell_dumps"))
            dumps_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_file = dumps_dir / f"provider_input_{timestamp}.txt"

            with open(input_file, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"Provider input saved to {input_file}")
        except Exception as e:
            logger.error(f"Failed to save input debug file: {str(e)}")

        try:
            contents = self._get_example_content()
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text),
                    ],
                ),
            )

            logger.info(f"Setting up generate_content_config (model: {self.model})")
            generate_content_config = types.GenerateContentConfig(
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                max_output_tokens=8192,
                response_mime_type="text/plain",
                system_instruction=self._get_system_instruction(),
            )

            logger.info("Calling Gemini API")
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=generate_content_config,
                )

                # Dump complete response for debugging
                self._dump_response(response)

                logger.info(f"Response received. Type: {type(response)}")

                if hasattr(response, "text"):
                    result = response.text
                    logger.info(
                        f"Response has text attribute. Result length: {len(result) if result else 0}"
                    )
                    if not result:
                        logger.warning("Response.text is empty or None")
                else:
                    logger.error("Response does not have text attribute")
                    # Try to extract text in alternative ways
                    if hasattr(response, "parts"):
                        parts_text = [
                            part.text
                            for part in response.parts
                            if hasattr(part, "text")
                        ]
                        result = "\n".join(parts_text)
                        logger.info(
                            f"Extracted text from parts. Result length: {len(result)}"
                        )
                    else:
                        logger.error("Cannot extract text from response")
                        # Try to convert the whole response to string
                        result = str(response)
                        logger.info(
                            f"Converted response to string. Result: {result[:100]}..."
                        )

                return result

            except Exception as e:
                logger.error(f"Error calling Gemini API: {type(e).__name__}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        except Exception as e:
            logger.error(
                f"Unexpected error in correct_text: {type(e).__name__}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _dump_response(self, response):
        """Dump response to a file for debugging."""
        try:
            # Create dumps directory if it doesn't exist
            dumps_dir = Path(os.path.expanduser("~/subspell_dumps"))
            dumps_dir.mkdir(exist_ok=True)

            # Create a timestamp for the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dump_file = dumps_dir / f"gemini_response_{timestamp}.txt"

            logger.info(f"Dumping response to {dump_file}")

            # Write response attributes to file
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write("=== GEMINI RESPONSE DUMP ===\n\n")
                f.write(f"Response type: {type(response)}\n\n")

                # Try to extract and write all attributes
                f.write("=== ATTRIBUTES ===\n")
                for attr in dir(response):
                    if not attr.startswith("_"):  # Skip private attributes
                        try:
                            value = getattr(response, attr)
                            # Handle method vs property
                            if not callable(value):
                                f.write(f"{attr}: {repr(value)}\n")
                        except Exception as e:
                            f.write(f"{attr}: Error accessing - {str(e)}\n")

                # Try to get .text property specifically
                f.write("\n=== TEXT PROPERTY ===\n")
                try:
                    if hasattr(response, "text"):
                        f.write(f"response.text: {repr(response.text)}\n")
                    else:
                        f.write("No .text property found\n")
                except Exception as e:
                    f.write(f"Error accessing .text: {str(e)}\n")

                # Try to get parts
                f.write("\n=== PARTS ===\n")
                try:
                    if hasattr(response, "parts"):
                        parts = response.parts
                        f.write(f"Number of parts: {len(parts)}\n")
                        for i, part in enumerate(parts):
                            f.write(f"\nPart {i}:\n")
                            f.write(f"  Type: {type(part)}\n")
                            for part_attr in dir(part):
                                if not part_attr.startswith("_"):
                                    try:
                                        part_value = getattr(part, part_attr)
                                        if not callable(part_value):
                                            f.write(
                                                f"  {part_attr}: {repr(part_value)}\n"
                                            )
                                    except Exception as e:
                                        f.write(
                                            f"  {part_attr}: Error accessing - {str(e)}\n"
                                        )
                    else:
                        f.write("No .parts property found\n")
                except Exception as e:
                    f.write(f"Error accessing parts: {str(e)}\n")

                # Try to convert to raw representation
                f.write("\n=== RAW STRING REPRESENTATION ===\n")
                try:
                    f.write(str(response))
                except Exception as e:
                    f.write(f"Error converting to string: {str(e)}\n")

                # Try dict representation via __dict__
                f.write("\n=== DICT REPRESENTATION ===\n")
                try:
                    if hasattr(response, "__dict__"):
                        f.write(repr(response.__dict__))
                    else:
                        f.write("Object has no __dict__ attribute")
                except Exception as e:
                    f.write(f"Error getting __dict__: {str(e)}\n")

            logger.info(f"Response dump completed to {dump_file}")
            return dump_file

        except Exception as e:
            logger.error(f"Failed to dump response: {str(e)}")
            logger.error(traceback.format_exc())
            return None
